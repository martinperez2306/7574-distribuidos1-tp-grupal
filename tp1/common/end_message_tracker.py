class EndMessageTracker():
    def __init__(self, nr_instances) -> None:
        self.nr_instances = nr_instances
        self.clients = {}

    def add_end_message(self, client_id, end_message_id):
        self.clients.setdefault(client_id, set())
        self.clients[client_id].add(end_message_id)

    def is_finished(self, client_id):
        return len(self.clients[client_id]) == self.nr_instances
