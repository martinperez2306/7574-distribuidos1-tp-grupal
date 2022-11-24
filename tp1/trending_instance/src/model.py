


class Grouper():
    def __init__(self):
        self.clients = {}

    def add_value(self, client_id, date, views):
        datem = date.strftime("%Y-%m-%d")

        self.clients.setdefault(client_id, {})

        dates = self.clients[client_id]
        dates.setdefault(datem, 0)
        dates[datem] += views

        return

    def len(self, client_id):
        return len(self.clients[client_id])

    def get_max(self, client_id):
        max_date = ''
        max_number = 0
        dates = self.clients[client_id]

        for date in dates:
            if (dates[date] > max_number):
                max_number = dates[date]
                max_date = date
        return max_date, max_number
