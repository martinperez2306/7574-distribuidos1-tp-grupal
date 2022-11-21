import time
import docker
import logging
from ctypes import c_bool, c_int
from multiprocessing import Process, Value

from src.bully_tcp_middleware import BullyTCPMiddleware
from src.election_message import AliveAnswerMessage, AliveMessage, CoordinatorMessage, ElectionAnswerMessage, ElectionMessage, ErrorMessage, LeaderElectionMessage, TimeoutMessage

NO_LEADER = -1

class BullyTCPWorker:
    """BullyTCPWorker\n
    This class represents worker with specific Bully Relationship.\n
    The Master is worker who has responsability to perform a certain activity.\n
    The Slaves are replicated workers to ensure the availability of the task to be executed.\n
    Implements Bully algorithm leader election.
    """
    def __init__(self, config_params, work_group) -> None:
        self.id = config_params['service_id']
        self.bully_id = int(config_params['instance_id'])
        self.bully_instances = int(config_params['watchers_instances'])
        self.check_retries = int(config_params['check_retries'])
        self.check_frecuency = int(config_params['check_frecuency'])
        self.leader_timeout = int(config_params['leader_timeout'])
        self.slave_timeout = int(config_params['slave_timeout'])
        self.election_timeout = int(config_params['election_timeout'])
        self.work_group = work_group
        self.bully_middleware = BullyTCPMiddleware(config_params, self.work_group)
        self.middleware_process: Process = None
        self.start_bully_process: Process = None
        self.check_process: Process = None
        self.docker = docker.from_env()
        ####CRITIC SECTION####
        self.running = Value(c_bool, False)
        self.leader = Value(c_int, NO_LEADER)
        ######################

    def start(self):
        """Start\n
            Starts Bully processes
            - Bully Middleware process (Backgroud process)
            - Bully Init process (Backgroud process)
            - Bully Check process (Backgroud process)\n
            Each process will have a copy of the middleware. 
        """
        logging.info("BullyTCPWorker started")
        self.running.value = True
        self.middleware_process = Process(target=self._start_middleware)
        self.middleware_process.start()
        self.start_bully_process = Process(target=self._start_bully)
        self.start_bully_process.start()
        self.check_process = Process(target=self._check_alive)
        self.check_process.start()
    
    def _start_middleware(self):
        """Start Middleware\n
            Starts Bully Middleware process and waits for Bully worker stop.\n
            This process has `bully_middleware` copy responsable to accept conections and handle messages.
        """
        self.bully_middleware.initialize()
        while self.running.value:
            self.bully_middleware.accept_connection(self._handle_message)
        self.bully_middleware.finalize()

    def _start_bully(self):
        """Start Bully\n
            This process has `bully_middleware` copy responsable to start bully algorithm.\n
            If process started has higher ID, takes the leadership and tells to other process. Otherwise it starts leader election.\n
            This process may run only once in bully worker startup.
        """
        if self.bully_id == (self.bully_instances -1):
            self._setme_as_leader()
        else:
            self._start_election()

    def _check_alive(self):
        """Check Alive\n
            This process has `bully middleware` copy responsible to check alives entities until bully worker is stopped.
            This process may run only once in bully worker startup.
            - Leader check
            - Slave check
        """
        while self.running.value:
            if (self.leader.value != NO_LEADER) and self.im_leader():
                self._check_slaves_alive()
            elif (self.leader.value != NO_LEADER) and not self.im_leader():
                self._check_leader_alive()
            time.sleep(self.check_frecuency)

    def _check_slaves_alive(self):
        logging.debug("Checking slaves alives")
        for instance_id in range(self.bully_instances):
            if instance_id != self.bully_id:
                checking_tries = 0
                message = AliveMessage(self.bully_id).to_string()
                while checking_tries < self.check_retries:
                    slave_response = self.bully_middleware.send(message, instance_id, self.slave_timeout, self._handle_message)
                    if not slave_response:
                        checking_tries+=1
                        time.sleep(self.check_frecuency)
                    else:
                        break 
                if checking_tries == self.check_retries:
                    logging.info("Slave [{}] is not responding".format(instance_id))
                    self.wake_up_slave(instance_id)

    def _check_leader_alive(self):
        """Check Leader Alive\n
            Here `bully middleware` copy is responsible to check alives start new election if leader is not responding.
        """
        logging.debug("Checking leader alives")
        checking_tries = 0
        message = AliveMessage(self.bully_id).to_string()
        while checking_tries < self.check_retries:
            leader_response = self.bully_middleware.send(message, self.leader.value, self.leader_timeout, self._handle_message)
            if not leader_response:
                checking_tries+=1
                time.sleep(self.check_frecuency)
            else:
                break 
        if checking_tries == self.check_retries:
            logging.info("Leader [{}] is not responding".format(self.leader.value))
            self._start_election()

    def wake_up_slave(self, instance_id):
        logging.info("Waking up instance with id [{}]".format(instance_id))
        service = self.work_group + "_" + str(instance_id)
        self.docker.api.stop(service)
        self.docker.api.start(service)

    def _start_election(self):
        """Start Election\n
           This method starts new leader election acording to Bully Algorithm.\n
           - Sends a Leader Election Message and waits for Answer Election Message
           - If no answer received, it proclaims himself as a leader
        """
        logging.info("Starting leader election")
        self.leader.value = NO_LEADER
        election = LeaderElectionMessage(self.bully_id)
        election_responses = self.bully_middleware.send_to_sups(election.to_string(), self.election_timeout, self._handle_message)
        if not any(election_responses):
            self._setme_as_leader()

    def _setme_as_leader(self):
        """Set me As Leader\n
           Proclaims himself as a leader.
        """
        logging.info("Setting me as leader and tell others")
        self.leader.value = self.bully_id
        election = CoordinatorMessage(self.bully_id)
        self.bully_middleware.send_to_all(election.to_string(), self.election_timeout, self._handle_message)

    def _handle_message(self, connection, message: str) -> bool:
        """Handle Message\n
           This method handle message from connection and returns boolean representation of handle.
           If handle successfully returns True otherwise returns False.
        """
        logging.debug('Handling Message [{}]'.format(message))
        election = ElectionMessage.of(message)
        if TimeoutMessage.is_election(election):
            logging.debug("Timeout message!")
            return False
        elif ErrorMessage.is_election(election):
            logging.debug("Error message!")
            return False
        elif AliveMessage.is_election(election):
            alive_answer_message = AliveAnswerMessage(self.bully_id).to_string()
            logging.debug("Responding alive message")
            self.bully_middleware.send_to_connection(alive_answer_message, connection)
        elif LeaderElectionMessage.is_election(election):
            logging.debug("Leader election in progress")
            self.leader.value = NO_LEADER
            election_answer_message = ElectionAnswerMessage(self.bully_id).to_string()
            self.bully_middleware.send_to_connection(election_answer_message, connection)
            self._start_election()
        elif AliveAnswerMessage.is_election(election):
            if self.im_leader():
                logging.debug("Slave is alive")
            else:
                logging.debug("Leader is alive")
        elif ElectionAnswerMessage.is_election(election):
            logging.debug("Election answer message receive")
        elif CoordinatorMessage.is_election(election):
            self.leader.value = election.id
            if self.im_leader():
                logging.debug("Coordination message answer message receive")
            else:
                logging.info("New Leader was selected [{}]".format(election.id))
                self.bully_middleware.send_to_connection(message, connection)
        return True

    def im_leader(self) -> bool:
        return (self.bully_id == self.leader.value)

    def stop(self):
        """Stop\n
            Stops bully worker and waits for all worker process to finish.
        """
        self.running.value = False
        self.start_bully_process.join()
        self.check_process.join()
        self.middleware_process.join()
        logging.info('BullyTCPWorker stopped')
