from common.middleware import Middleware

FILTERED_LIKES_EXCHANGE = 'filtered_exchange'
RESULTS_QUEUE = 'results_queue'
LIKES_FILTER_RESULTS = 'likes_filters_tag_unique'

class TagUniqueMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.queue_declare(
            queue=RESULTS_QUEUE, durable=True)

        self.channel.queue_declare(
            queue=LIKES_FILTER_RESULTS, durable=True)

        self.channel.queue_bind(
            exchange=FILTERED_LIKES_EXCHANGE, queue=LIKES_FILTER_RESULTS)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(LIKES_FILTER_RESULTS, callback)
        self.channel.start_consuming()

    def send_result_message(self, message):
        super().send_message(RESULTS_QUEUE, message)
