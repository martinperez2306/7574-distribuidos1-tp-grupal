import logging
from common.middleware import Middleware

WATCHER_EXCHANGE = 'watcher_exchange'
WATCHER_QUEUE = 'watcher_queue'

logging.getLogger("pika").propagate = False

class WatcherMiddlware(Middleware):
    def __init__(self, service_id) -> None:
        super().__init__()

        self.queue = WATCHER_QUEUE + "_" + service_id
        self.channel.exchange_declare(exchange=WATCHER_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(self.queue)
        self.channel.queue_bind(exchange=WATCHER_EXCHANGE, queue=self.queue)

        self.channel.basic_qos(prefetch_count=1)

    def accept_heartbeats(self, callback):
        # Get ten messages and break out
        for method_frame, properties, body in self.channel.consume(queue=self.queue, inactivity_timeout=10):

            heartbeat = None

            if method_frame is None and properties is None and body is None:
                logging.info("Timeout for receive message")

            else:
                # Display the message parts
                logging.info(method_frame)
                logging.info(properties)
                logging.info(body)
                heartbeat = body.decode()
                # Acknowledge the message
                self.channel.basic_ack(method_frame.delivery_tag)

            callback(heartbeat)

    def stop(self):
        # Cancel the consumer and return any pending messages
        requeued_messages = self.channel.cancel()
        logging.info('Requeued %i messages' % requeued_messages)
        # Close the channel and the connection
        self.channel.close()
        self.connection.close()