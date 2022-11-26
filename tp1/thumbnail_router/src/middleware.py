from common.middleware import Middleware

THUMBNAIL_EXCHANGE = 'thumbnail_exchange'
DISTRIBUTION_EXCHANGE = 'distribution_exchange'
DISTRIBUTION_QUEUE = 'distribution_thumbnail_router'

class ThumbnailRouterMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.exchange_declare(exchange=THUMBNAIL_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=DISTRIBUTION_QUEUE, durable=True)

        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=DISTRIBUTION_QUEUE)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(DISTRIBUTION_QUEUE, callback)
        self.channel.start_consuming()

    def send_video_message(self, message, id):

        super().send_to_exchange(THUMBNAIL_EXCHANGE, id, message)
