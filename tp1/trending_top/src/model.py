class ResultRepository():
    def __init__(self):
        self.clients = {}
        

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
    
    def results_len(self, client_id):
        client = self.clients[client_id]
        return len(client['responses'])

    def get_date(self, client_id):
        client = self.clients[client_id]
        return client['date']
