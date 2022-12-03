import json
import os
import logging

TOTAL_WORKFLOWS = 3

STORE_PATH = './storage/clients.json'


class ClientConnections():
    def __init__(self) -> None:
        self.clients = {}
        self._load()

    def accept_client(self, client_id):
        self.clients[client_id] = []
        self._persist()

    def len(self):
        return len(self.clients)

    def _persist(self):
        with open(STORE_PATH, 'w') as f:
            json.dump(self.clients, f)

    def _load(self):

        if os.path.exists(STORE_PATH):
            logging.info('Previous Clients File Found')
            with open(STORE_PATH) as f:
                self.clients = json.load(f)

    def remove_client(self, client_id):
        self.clients.pop(client_id, None)
        self._persist()

    def save_result(self, client_id, result_id):
        if not result_id in self.clients[client_id]:
            self.clients[client_id].append(result_id)
            self._persist()

    def is_client_finished(self, client_id):
        return len(self.clients[client_id]) == TOTAL_WORKFLOWS
