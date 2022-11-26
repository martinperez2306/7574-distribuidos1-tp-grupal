class EndResultsRepository():
    def __init__(self) -> None:
        self.clients = {}
    
    def add_end_result(self, client_id, instance_id):
        self.clients.setdefault(client_id, set())
        responses = self.clients[client_id]
        responses.add(instance_id)

    def len_responses(self, client_id):
        self.clients.setdefault(client_id, set())
        responses = self.clients[client_id]
        return len(responses)
