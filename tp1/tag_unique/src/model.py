class ResultRepository():
    def __init__(self):
        self.items = {}

    def add_element(self, client_id, element):
        self.items[client_id].add(element)

    def check_element(self, client_id, element):
        self.items.setdefault(client_id, set())
        return element in self.items[client_id]
