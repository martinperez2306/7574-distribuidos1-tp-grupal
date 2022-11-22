import logging
import socket
from src.election_message import ELECTION_LENGTH_MESSAGE, ErrorMessage, TimeoutMessage

BUFFER_SIZE = 1024
ENCODING = "utf-8"

class BullyTCPMiddleware(object):
    """BullyTCPMiddlware\n
    This class provides a communication layer between bully workers.\n
    The communication can be 
        * Master - Slave
        * Slave - Slave
    """

    def __init__(self, config_params, work_group) -> None:
        """
        Creates a new istance of BullyTCPMiddlware
        """
        self.port = int(config_params['service_port'])
        self.bully_id = int(config_params['instance_id'])
        self.bully_instances = int(config_params['watchers_instances'])
        self.listening_timeout = float(config_params['bully_listening_timeout'])
        self.work_group = work_group
        self.server_socket = None
    
    def initialize(self):
        logging.info("BullyTCPMiddlware initialized")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(self.bully_instances)

    def accept_connection(self, callback):
        logging.debug("Accept connections in port [{}]".format(self.port))
        callback_result = None
        self.server_socket.settimeout(self.listening_timeout)
        try:
            connection, _addr = self.server_socket.accept()
            callback_result = self._handle_connection(connection, callback)
        except socket.timeout as timeout:
            pass #Timeout await connections is expected
        except socket.error as error:
            logging.error("Error while accept connection in server socket {}. Error: {}".format(self.server_socket, error))
            self.server_socket.close()
        self.server_socket.settimeout(None)
        return callback_result
            
    def _handle_connection(self, connection: socket.socket, callback):
        logging.debug("Handling connection [{}]".format(connection))
        expected_length_message = ELECTION_LENGTH_MESSAGE + len(str(self.bully_instances))
        message = self._recv(connection, expected_length_message)
        return callback(connection, message)

    def send_to_infs(self, message: str, timeout: float, callback) -> list:
        instances = range(self.bully_id)
        return self._send_to(message, instances, timeout, callback)

    def send_to_sups(self, message: str, timeout: float, callback) -> list:
        instances = range(self.bully_id, self.bully_instances)
        return self._send_to(message, instances, timeout, callback)

    def send_to_all(self, message: str, timeout: float, callback) -> list:
        instances = range(self.bully_instances)
        return self._send_to(message, instances, timeout, callback)
    
    def _send_to(self, message: str, instances: list['int'], timeout: float, callback) -> list:
        callback_results = list()
        for instance_id in instances:
            if instance_id != self.bully_id:
                callback_result = self.send(message, instance_id, timeout, callback)
                callback_results.append(callback_result)
        return callback_results

    def send(self, message: str, instance_id: int, timeout: float, callback):
        """Send\n
            Create connection and send message to a instance.\n
            If a `timeout` is specified, it waits to receive a response in that period of time.\n
            Returns callback's result.
        """
        callback_result = None
        host = self.work_group + "_" + str(instance_id)
        port = self.port
        logging.debug("Sending [{}] to Host [{}] and Port [{}]".format(message, host, port))
        try:
            with socket.create_connection((host, port)) as connection:
                connection.sendall(message.encode(ENCODING))
                expected_length_message = ELECTION_LENGTH_MESSAGE + len(str(self.bully_instances))
                response = self._recv_timeout(connection, expected_length_message, timeout)
                callback_result = callback(connection, response)
        except socket.error as error:
            logging.error("Error while create connection to socket. Error: {}".format(error))
        return callback_result

    def send_to_connection(self, message: str, connection: socket.socket):
        """Send To Connection\n
            Sends message to existing connection
        """
        connection.sendall(message.encode(ENCODING))

    def _recv(self, connection: socket.socket, expected_length_message: int) -> str:
        data = b''
        while len(data) < expected_length_message:
            try:
                data += connection.recv(BUFFER_SIZE)
            except socket.error as error:
                logging.error("Error while recv data from connection {}. Error: {}".format(connection, error))
                return ErrorMessage().to_string()
        return data.decode(ENCODING)

    def _recv_timeout(self, connection: socket.socket, expected_length_message: int, timeout: float) -> str:
        data = b''
        connection.settimeout(timeout)
        while len(data) < expected_length_message:
            try:
                data += connection.recv(BUFFER_SIZE)
            except socket.timeout as timeout:
                logging.error("Timeout for recv data from connection {}. Error: {}".format(connection, timeout))
                return TimeoutMessage().to_string()
            except socket.error as error:
                logging.error("Error while recv data from connection {}. Error: {}".format(connection, error))
                return ErrorMessage().to_string()
        connection.settimeout(None)
        return data.decode(ENCODING)

    def finalize(self):
        self.server_socket.close()
        logging.info('BullyTCPMiddlware finalized')