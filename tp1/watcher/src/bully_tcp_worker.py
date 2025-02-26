import time
import docker
import logging
from ctypes import c_bool, c_int
from multiprocessing import Condition, Process, Queue, Value

from src.bully_tcp_middleware import BullyTCPMiddleware
from src.election_message import AliveAnswerMessage, AliveMessage, CoordinatorMessage, ElectionAnswerMessage, ElectionMessage, EmptyMessage, ErrorMessage, LeaderElectionMessage, TimeoutMessage

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
        self.check_retries = int(config_params['bully_check_retries'])
        self.check_frecuency = int(config_params['bully_check_frecuency'])
        self.leader_timeout = float(config_params['bully_leader_timeout'])
        self.slave_timeout = float(config_params['bully_slave_timeout'])
        self.election_timeout = float(config_params['bully_election_timeout'])
        self.work_group = work_group
        self.docker = docker.from_env()
        self.bully_middleware = BullyTCPMiddleware(config_params, self.work_group)
        self.bully_action_process: Process = None
        self.bully_listening_process: Process = None
        self.bully_init_process: Process = None
        self.check_process: Process = None
        ####CRITICAL SECTION####
        self.running = Value(c_bool, False)
        self.leader = Value(c_int, NO_LEADER)
        self.connection_action_queue = Queue()
        self.is_election_in_progress = Value(c_bool, False)
        self.election_condition = Condition()
        ######################

    def start(self):
        """Start\n
            Starts Bully processes
            - Bully Action process (Backgroud process)
            - Bully Listening process (Backgroud process)
            - Bully Init process (Backgroud process)
            - Bully Check process (Backgroud process)\n
            Each process will have a copy of the middleware. 
        """
        logging.info("BullyTCPWorker started")
        self.running.value = True
        self.bully_action_process = Process(target=self._perform_connection_action)
        self.bully_action_process.start()
        self.bully_listening_process = Process(target=self._accept_connections)
        self.bully_listening_process.start()
        self.bully_init_process = Process(target=self._start_bully)
        self.bully_init_process.start()
        self.check_process = Process(target=self._check_alive)
        self.check_process.start()
    
    def _perform_connection_action(self):
        """Handle Event \n
            Performs a post-connection action according to the message received by a connection 
        """
        while self.running.value:
            connection_message = self.connection_action_queue.get()
            self._perform_post_connection_action(connection_message)

    def _perform_post_connection_action(self, election_message):
        if election_message:
            if LeaderElectionMessage.is_election(election_message):
                self._start_election(False)
            elif ElectionAnswerMessage.is_election(election_message):
                with self.election_condition:
                    self.election_condition.wait(timeout=self.election_timeout)
                    if (self.leader == NO_LEADER and self.is_election_in_progress.value):
                        self._start_election(True)

    def _accept_connections(self):
        """Accept Connections\n
            Initialize Bully Middleware and waits for Bully worker stop.\n
            This process has `bully_middleware` copy responsable to accept conections and handle messages.\n
            Sends connection message to Action Queue in order to perform corresponding action.
        """
        self.bully_middleware.initialize()
        while self.running.value:
            connection_message = self.bully_middleware.accept_connection(self._handle_message)
            if connection_message:
                self.connection_action_queue.put(connection_message)
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
            self._start_election(False)

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
                        time.sleep(self.slave_timeout)
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
                time.sleep(self.leader_timeout)
            else:
                break 
        if checking_tries == self.check_retries:
            logging.info("Leader [{}] is not responding".format(self.leader.value))
            self._start_election(False)

    def wake_up_slave(self, instance_id):
        if self.im_leader():
            logging.info("Waking up instance with id [{}]".format(instance_id))
            service = self.work_group + "_" + str(instance_id)
            self.docker.api.stop(service)
            self.docker.api.start(service)

    def _handle_message(self, connection, message: str):
        """Handle Message\n
           This method handle message from connection and performs some actions for that connection.\n
           If handle successfully returns same `ElectionMessage` otherwise returns `None`.\n
           Not successfully cases are
           - TimeoutMessage
           - ErrorMessage
        """
        logging.debug('Handling Message [{}]'.format(message))
        election_message = ElectionMessage.of(message)
        if TimeoutMessage.is_election(election_message):
            logging.error("Timeout message! [{}]".format(message))
            return None
        elif ErrorMessage.is_election(election_message):
            logging.error("Error message! [{}]".format(message))
            return None
        elif AliveMessage.is_election(election_message):
            alive_answer_message = AliveAnswerMessage(self.bully_id).to_string()
            logging.debug("Responding alive message")
            self.bully_middleware.send_to_connection(alive_answer_message, connection)
        elif AliveAnswerMessage.is_election(election_message):
            if self.im_leader():
                logging.debug("Slave [{}] is alive!".format(election_message.id))
            else:
                logging.debug("Leader [{}] is alive!".format(election_message.id))
        elif LeaderElectionMessage.is_election(election_message):
            logging.info("Responding leader election [{}]".format(message))
            election_answer_message = ElectionAnswerMessage(self.bully_id).to_string()
            self.bully_middleware.send_to_connection(election_answer_message, connection)
        elif ElectionAnswerMessage.is_election(election_message):
            logging.info("Election answer message receive [{}]".format(message))
        elif CoordinatorMessage.is_election(election_message):
            self.leader.value = election_message.id
            self.is_election_in_progress.value = False
            if self.im_leader():
                logging.info("Coordination answer message receive {}".format(message))
            else:
                logging.info("New Leader was selected [{}]".format(election_message.id))
                self.bully_middleware.send_to_connection(message, connection)
            with self.election_condition:
                self.election_condition.notify_all()
        return election_message

    def _start_election(self, force: bool):
        """Start Election\n
           This method starts new leader election acording to Bully Algorithm.\n
           - If has not already started an election, sends a Leader Election Message and waits for Answer Election Message
           - If no answer received, it proclaims himself as a leader
           - If `force` is provided, forces the leader election even if it has already started
        """
        if self.is_election_in_progress.value and not force:
            logging.info("Leader election in progress")
            return
        logging.info("Starting leader election")
        self.is_election_in_progress.value = True
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
        self.is_election_in_progress.value = False
        election = CoordinatorMessage(self.bully_id)
        self.bully_middleware.send_to_all(election.to_string(), self.election_timeout, self._handle_message)

    def im_leader(self) -> bool:
        return (self.bully_id == self.leader.value)

    def stop(self):
        """Stop\n
            Stops bully worker and waits for all worker process to finish.
        """
        self.running.value = False
        self.check_process.join()
        self.bully_init_process.join()
        self.bully_listening_process.join()
        self.connection_action_queue.put(EmptyMessage())
        self.bully_action_process.join()
        logging.info('BullyTCPWorker stopped')
