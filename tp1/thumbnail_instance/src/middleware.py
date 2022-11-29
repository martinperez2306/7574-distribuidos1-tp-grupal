from common.middleware import Middleware

CATEGORIES_COUNT_EXCHANGE = 'categories_count_exchange'
THUMBNAIL_EXCHANGE = 'thumbnail_exchange'
DOWNLOAD_QUEUE = 'download_queue'
PREFIX_CATEGORIES_COUNT_RESULTS = 'categories_count_thumbnail_instance_'
PREFIX_THUMBNAIL_INSTANCE_QUEUE = 'thumbnail_instance_'


class ThumbnailInstanceMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=THUMBNAIL_EXCHANGE,
                                      exchange_type='direct')

        self.channel.exchange_declare(exchange=CATEGORIES_COUNT_EXCHANGE,
                                      exchange_type='fanout')

        self.category_count_input = PREFIX_CATEGORIES_COUNT_RESULTS + instance_nr 
        # Bind results to exchange so we get category count in all instances.
        self.channel.queue_declare(
            queue=self.category_count_input, durable=True)

        self.channel.queue_bind(
            exchange=CATEGORIES_COUNT_EXCHANGE, queue=self.category_count_input, routing_key='')

        self.channel.queue_declare(queue=DOWNLOAD_QUEUE, durable=True)
        
        self.recv_queue = PREFIX_THUMBNAIL_INSTANCE_QUEUE + instance_nr
        self.channel.queue_declare(queue=self.recv_queue, durable=True)

        self.channel.queue_bind(
            exchange=THUMBNAIL_EXCHANGE, queue=self.recv_queue, routing_key=instance_nr)

    def recv_category_count(self, callback):
        self.cat_count_tag = super().recv_message(self.category_count_input, callback)
        
    def stop_recv_category_count(self):
        super().stop_recv_message(consumer_tag=self.cat_count_tag)

    def recv_video_message(self, callback):\
        self.vid_msg_tag = super().recv_batch_message(self.recv_queue, callback)

    def send_result_message(self, message):
        super().send_message(DOWNLOAD_QUEUE, message)
