from common.middleware import Middleware

CATEGORIES_EXCHANGE = 'categories_exchange'
DROPPER_INPUT_QUEUE = 'dropper_input'
CLIENT_ACCEPT_QUEUE = 'client_accept'


class ClientMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.exchange_declare(exchange=CATEGORIES_EXCHANGE,
                                      exchange_type='fanout')
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE)

    def send_category_message(self, message):
        super().send_to_exchange(CATEGORIES_EXCHANGE, '', message)

    def send_video_message(self, message):
        super().send_message(DROPPER_INPUT_QUEUE, message)

    def send_handshake_message(self, message):
        super().send_message(CLIENT_ACCEPT_QUEUE, message)

    def recv_result_message(self, client_id, callback):
        self.channel.queue_declare(
            queue=client_id, exclusive=True)
        self.result_tag = super().recv_message(client_id, callback)
        self.channel.start_consuming()

    def stop_recv_result_message(self):
        super().stop_recv_message(self.result_tag)
    
    