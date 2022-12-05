import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult3, Result3
from .model import ResultRepository

class TrendingTop(HeartbeathedWorker):
    def __init__(self, middleware, trending_instances) -> None:
        super().__init__(middleware)
        self.model = ResultRepository()
        self.trending_instances = trending_instances
        
    def run(self):
        self.middleware.recv_result_message(self.recv_results)

    def recv_results(self, message):

        message = Result3.decode(message)
        instance_id = message.message_id
        client_id = message.client_id
        values = message.content.split(',')
        date = values[0]
        views = int(values[1])

        self.model.add_element(client_id, instance_id, date, views)

        if (self.model.results_len(client_id) == self.trending_instances):
            message = Result3(message.client_id, self.model.get_date(client_id), self.model.get_date(client_id))
            
            self.middleware.send_result_message(message.pack())

            end_message = EndResult3(message.client_id)
            self.middleware.send_result_message(end_message.pack())
            
