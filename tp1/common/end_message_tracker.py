import json
import logging
import os 

STORE_PATH = './storage/end_message.json'


class EndMessageTracker():
    def __init__(self, nr_instances) -> None:
        self.nr_instances = nr_instances
        self.clients = {}
        self._loads()

    def add_end_message(self, client_id, end_message_id):
        self.clients.setdefault(client_id, set())
        self.clients[client_id].add(end_message_id)
        self._persist()

    def is_finished(self, client_id):
        return len(self.clients[client_id]) == self.nr_instances

    def _persist(self):
        r = dict(self.clients)
        for client in r:
            r[client] = list(r[client])

        with open(STORE_PATH, 'w') as f:
            json.dump(r, f)
        

    def _loads(self):
        try:
            if os.path.exists(STORE_PATH):
                with open(STORE_PATH) as f:
                    data = json.load(f)
                    for key in data:
                        self.clients[key] = set(data[key])
        except ValueError:
            logging.info('No previous End Message Tracking File')
