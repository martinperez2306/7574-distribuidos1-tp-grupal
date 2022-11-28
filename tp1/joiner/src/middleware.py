from common.middleware import Middleware
import os 

CATEGORIES_COUNT_EXCHANGE = 'categories_count_exchange'
CATEGORIES_EXCHANGE = 'categories_exchange'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'
JOINER_EXCHANGE = 'joiner_exchange'

CATEGORIES_QUEUE_PREFIX = 'categories_'
PREFIX_JOINER_INPUT = 'joiner_input_'

class JoinerMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()
        self.joiner_input = PREFIX_JOINER_INPUT + instance_nr

        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        
        self.channel.exchange_declare(exchange=CATEGORIES_COUNT_EXCHANGE,
                                      exchange_type='fanout')
        
        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')
        
        self.channel.exchange_declare(exchange=JOINER_EXCHANGE,
                                      exchange_type='direct')

        
        self.categories_queue = CATEGORIES_QUEUE_PREFIX + instance_nr

        self.channel.queue_declare(queue=self.categories_queue, durable=True)

        self.channel.queue_bind(
            exchange=CATEGORIES_EXCHANGE, queue=self.categories_queue)

        self.channel.queue_declare(
            queue=self.joiner_input, durable=True)

        # Bind Data messages sent to instance nr
        self.channel.queue_bind(
            exchange=JOINER_EXCHANGE, queue=self.joiner_input, routing_key=instance_nr)
        
        # Bind End message
        self.channel.queue_bind(
            exchange=JOINER_EXCHANGE, queue=self.joiner_input, routing_key='end')
            
        self.channel.basic_qos(prefetch_count=30)

    def recv_category_message(self, callback):
        self.cat_msg_tag = super().recv_message(self.categories_queue, callback)


    def recv_video_message(self, callback):
        self.vid_msg_tag = super().recv_message(self.joiner_input, callback)
        
    def send_category_count(self, message):
        super().send_to_exchange(CATEGORIES_COUNT_EXCHANGE, '', message)

    def send_video_message(self, message):
        super().send_to_exchange(DISTRIBUTION_EXCHANGE, '', message)

    
