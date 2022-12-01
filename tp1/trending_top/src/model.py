
import json
import logging
import os

STORE_PATH = './storage/results_message.json'


class ResultRepository():
    def __init__(self):
        self.clients = {}

        self._loads()

    def add_element(self, client_id, instance_id, date, views):
        self.clients.setdefault(client_id, {
            'responses': set(),
            'views': 0,
            'date': ''
        })

        client = self.clients[client_id]

        if (views > client['views']):
            client['views'] = views
            client['date'] = date

        client['responses'].add(instance_id)
        self._persist()

    def results_len(self, client_id):
        client = self.clients[client_id]
        return len(client['responses'])

    def get_date(self, client_id):
        client = self.clients[client_id]
        return client['date']

    def _persist(self):
        r = {}
        for client in self.clients:
            r[client] = dict(self.clients[client])
            r[client]['responses'] = list(r[client]['responses'])

        with open(STORE_PATH, 'w') as f:
            json.dump(r, f)
        

    def _loads(self):
        try:
            if os.path.exists(STORE_PATH):
                with open(STORE_PATH) as f:
                    data = json.load(f)
                    for key in data:
                        data[key]['responses'] = set(data[key]['responses'])
                        self.clients[key] = data[key]
        except ValueError:
            logging.info('No previous End Message Tracking File')
