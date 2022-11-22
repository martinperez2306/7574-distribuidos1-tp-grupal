TOTAL_WORKFLOWS = 3


class ClientConnections():
    def __init__(self) -> None:
        self.clients = {}

    def accept_client(self, client_id):
        self.clients[client_id] = []

    def len(self):
        return len(self.clients)

    def flush(self):
        pass
        # Logic to persist data here

    def remove_client(self, client_id):
        del self.clients[client_id]

    def save_result(self, client_id, result_id):
        if not result_id in self.clients[client_id]:
            self.clients[client_id].append(result_id)

    def is_client_finished(self, client_id):
        return len(self.clients[client_id]) == TOTAL_WORKFLOWS
