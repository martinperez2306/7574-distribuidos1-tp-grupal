import logging
from common.middleware import Middleware
from src.heartbeats import SERVICE_HEARTBEAT_TIMEOUT

WATCHER_EXCHANGE = 'watcher_exchange'
WATCHER_QUEUE = 'watcher_queue'

class WatcherMiddlware(Middleware):
    def __init__(self, service_id) -> None:
        super().__init__()
        self.running = False
        self.queue = WATCHER_QUEUE + "_" + service_id
        self.channel.exchange_declare(exchange=WATCHER_EXCHANGE, exchange_type='fanout')
        self.channel.queue_declare(self.queue)
        self.channel.queue_bind(exchange=WATCHER_EXCHANGE, queue=self.queue)

        

    def run(self):
        self.running = True

    def accept_heartbeats(self, callback):
        # Get ten messages and break out
        for method_frame, properties, body in self.channel.consume(queue=self.queue, inactivity_timeout=SERVICE_HEARTBEAT_TIMEOUT):
            if not self.running:
                logging.info("Breacking consume loop")
                break

            heartbeat = None

            if method_frame is None and properties is None and body is None:
                logging.info("Timeout for receive Service hearbeat")

            else:
                # Display the message parts
                logging.debug("Method Frame [{}]".format(method_frame))
                logging.debug("Properties [{}]".format(properties))
                logging.debug("Message Body [{}]".format(body))
                heartbeat = body.decode()
                # Acknowledge the message
                self.channel.basic_ack(method_frame.delivery_tag)

            callback(heartbeat)
        # Close the channel and the connection
        self.channel.close()
        super().close_connection()

    def stop(self):
        self.running = False
        # Cancel the consumer and return any pending messages
        requeued_messages = self.channel.cancel()
        logging.info('Requeued %i messages for Watcher Middleware' % requeued_messages)
        logging.info('WatcherMiddlware stopped')
        