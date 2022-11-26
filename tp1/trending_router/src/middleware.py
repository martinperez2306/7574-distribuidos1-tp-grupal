from common.middleware import Middleware

TRENDING_EXCHANGE = 'trending_exchange'
FILTERED_LIKES_EXCHANGE = 'filtered_exchange'
TRENDING_RESULTS = 'filter_trending_route'

class TrendingRouterMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.exchange_declare(exchange=TRENDING_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=TRENDING_RESULTS, durable=True)

        self.channel.queue_bind(
            exchange=FILTERED_LIKES_EXCHANGE, queue=TRENDING_RESULTS)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(TRENDING_RESULTS, callback)
        self.channel.start_consuming()

    def send_video_message(self, message, id):

        super().send_to_exchange(TRENDING_EXCHANGE, id, message)
