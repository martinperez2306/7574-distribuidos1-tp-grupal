from common.middleware import Middleware
import os 
import logging

CATEGORIES_EXCHANGE = 'categories_exchange'
INPUT_EXCHANGE = 'input_exchange'
CLIENT_ACCEPT_QUEUE = 'client_accept'


class ClientMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        
        self.nr_output_instances = int(os.environ['OUTPUT_INSTANCES'])
        
        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        
        self.channel.exchange_declare(exchange=INPUT_EXCHANGE,
                                      exchange_type='direct')

    def send_category_message(self, message):
        super().send_to_exchange(CATEGORIES_EXCHANGE, '', message)

    def send_video_message(self, message, message_id):
        instance_nr = hash(message_id) % self.nr_output_instances
        
        super().send_to_exchange(INPUT_EXCHANGE, str(instance_nr), message)

    def send_end_message(self, message):
        logging.info(f'Send end message')
        super().send_to_exchange(INPUT_EXCHANGE,'end', message)

    def send_handshake_message(self, message):
        super().send_message(CLIENT_ACCEPT_QUEUE, message)

    def recv_result_message(self, client_id, callback):
        self.channel.queue_declare(
            queue=client_id, exclusive=True)
        self.result_tag = super().recv_message(client_id, callback)
    

    def stop_recv_result_message(self):
        super().stop_recv_message(self.result_tag)
    
    