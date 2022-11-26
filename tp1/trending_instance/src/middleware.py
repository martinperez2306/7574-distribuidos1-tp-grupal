from common.middleware import Middleware

TRENDING_EXCHANGE = 'trending_exchange'
TRENDING_TOP_QUEUE = 'trending_top_queue'
PREFIX_TRENDING_INSTANCE_QUEUE = 'trending_instance_'

class TrendingInstanceMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.channel.exchange_declare(exchange=TRENDING_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(queue=TRENDING_TOP_QUEUE, durable=True)

        self.trending_instance_input = PREFIX_TRENDING_INSTANCE_QUEUE + instance_nr
        self.channel.queue_declare(queue=self.trending_instance_input, durable=True)


        self.channel.queue_bind(
            exchange=TRENDING_EXCHANGE, queue=self.trending_instance_input, routing_key=instance_nr)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.trending_instance_input, callback)
        self.channel.start_consuming()

    def send_result_message(self, message):

        super().send_message(TRENDING_TOP_QUEUE, message)
