from common.middleware import Middleware

DISTRIBUTION_EXCHANGE = 'distribution_exchange'
FILTERED_LIKES_EXCHANGE = 'filtered_exchange'
LIKES_QUEUE = 'likes_queue_'


class LikesFilterMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()

        self.likes_input = LIKES_QUEUE + instance_nr

        self.channel.exchange_declare(exchange=DISTRIBUTION_EXCHANGE,
                                      exchange_type='topic')

        self.channel.exchange_declare(exchange=FILTERED_LIKES_EXCHANGE,
                                      exchange_type='fanout')

        self.channel.queue_declare(
            queue=self.likes_input, durable=True)

        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=self.likes_input, routing_key=f'{instance_nr}.*')
        
        self.channel.queue_bind(
            exchange=DISTRIBUTION_EXCHANGE, queue=self.likes_input, routing_key='end')

        

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.likes_input, callback)
        self.channel.start_consuming()

    def send_video_message(self, message):
        super().send_to_exchange(FILTERED_LIKES_EXCHANGE, '', message)

    
