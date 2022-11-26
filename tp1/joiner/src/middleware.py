from common.middleware import Middleware
import os 

CATEGORIES_COUNT_EXCHANGE = 'categories_count_exchange'
CATEGORIES_EXCHANGE = 'categories_exchange'
CATEGORIES_QUEUE_PREFIX = 'categories_'
VIDEO_DATA_QUEUE = 'video_data'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'


class JoinerMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.exchange_declare(exchange=CATEGORIES_COUNT_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')
        
        self.categories_queue = CATEGORIES_QUEUE_PREFIX + os.environ['SERVICE_ID']

        self.channel.queue_declare(queue=self.categories_queue, durable=True)

        self.channel.queue_bind(
            exchange=CATEGORIES_EXCHANGE, queue=self.categories_queue)

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE, durable=True)

        self.channel.basic_qos(prefetch_count=30)

    def recv_category_message(self, callback):
        self.cat_msg_tag = super().recv_message(self.categories_queue, callback)


    def recv_video_message(self, callback):
        self.vid_msg_tag = super().recv_message(VIDEO_DATA_QUEUE, callback)
        
    def send_category_count(self, message):
        super().send_to_exchange(CATEGORIES_COUNT_EXCHANGE, '', message)

    def send_video_message(self, message):
        super().send_to_exchange(DISTRIBUTION_EXCHANGE, '', message)

    
