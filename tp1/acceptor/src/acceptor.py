import logging
import time
from common.heartbeathed_worker import HeartbeathedWorker
from common.constants import DATA_SUBFIX
from src.client_connections import ClientConnections
from common.message import MessageHandshake, EndResult1, EndResult2, EndResult3, BaseMessage

MAX_CLIENTS = 5


class Acceptor(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.clients = ClientConnections()

    def run(self):
        self.middleware.recv_results_messages(self.on_result_message)
        self.middleware.recv_client_messages(self.on_client_message)
        self.middleware.consume()

    def on_client_message(self, message):

        if (not MessageHandshake.is_message(message)):
            return

        parsed_message = MessageHandshake.decode(message)

        self.clients.accept_client(parsed_message.client_id)
        self.clients.flush()

        self.middleware.send_result(
            parsed_message.client_id, message)

        if (self.clients.len() == MAX_CLIENTS):
            self.stop_recv_client_messages()

    def on_result_message(self, message):
        
        end_result = None
        base_message, _ = BaseMessage.decode(message)

        if (EndResult1.is_message(message)):
            end_result = 1

        if (EndResult2.is_message(message)):
            end_result = 2

        if (EndResult3.is_message(message)):
            end_result = 3

        if (end_result is not None):
            self.clients.save_result(base_message.client_id, end_result)

        self.middleware.send_result(base_message.client_id, message)
