from common.middleware import Middleware

CLIENT_ACCEPT_QUEUE = 'client_accept'
RESULTS_QUEUE = 'results_queue'


class AcceptorMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=CLIENT_ACCEPT_QUEUE, durable=True)

        self.channel.queue_declare(
            queue=RESULTS_QUEUE, durable=True)
        self.channel.basic_qos(prefetch_count=30)

    def recv_results_messages(self, callback):
        self.results_tag = super().recv_message(RESULTS_QUEUE, callback)

    def recv_client_messages(self, callback):
        self.client_tag = super().recv_message(CLIENT_ACCEPT_QUEUE, callback)

    def send_result(self, client_id, message):
        super().send_message(client_id, message)

    def stop_recv_client_messages(self):
        self.stop_recv_message(self.client_tag)
