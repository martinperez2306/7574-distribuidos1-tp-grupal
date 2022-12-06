from common.middleware import Middleware

THUMBNAIL_EXCHANGE = 'thumbnail_exchange'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'
DISTRIBUTION_QUEUE = 'thumbnail_router_'

class ThumbnailRouterMiddlware(Middleware):
    def __init__(self, instance_n) -> None:
        super().__init__()
        self.input_data = DISTRIBUTION_QUEUE + instance_n
        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='topic')

        self.channel.exchange_declare(exchange=THUMBNAIL_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=self.input_data, durable=True)

        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=self.input_data, routing_key=f'*.{instance_n}')
        
        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=self.input_data, routing_key=f'end')

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.input_data, callback)
        self.channel.start_consuming()

    def send_video_message(self, message, id):

        super().send_to_exchange(THUMBNAIL_EXCHANGE, id, message)
