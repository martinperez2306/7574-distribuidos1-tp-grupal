import logging
import os
import signal
import pika

from src.heartbeats import Heartbeats

WATCHER_QUEUE = "watcher_queue"

class Watcher:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None
        self.tries = 0
        self.heartbeats = Heartbeats()
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)


    def start(self):
        host = os.environ['RABBIT_SERVER_ADDRESS']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host))

        self.channel = self.connection.channel()

        self.channel.queue_declare(
                queue=WATCHER_QUEUE)

        # Get ten messages and break out
        for method_frame, properties, body in self.channel.consume(queue=WATCHER_QUEUE, inactivity_timeout=10):

            if method_frame is None and properties is None and body is None:
                logging.info("Timeout for receive message")

            else:
                # Display the message parts
                logging.info(method_frame)
                logging.info(properties)
                logging.info(body)

                # Acknowledge the message
                self.channel.basic_ack(method_frame.delivery_tag)

            self.heartbeats.hearbeat(body)
            self.heartbeats.check_services()

        self.close()
    
    def close(self):
        # Cancel the consumer and return any pending messages
        requeued_messages = self.channel.cancel()
        logging.info('Requeued %i messages' % requeued_messages)
        # Close the channel and the connection
        self.channel.close()
        self.connection.close()

    def exit_gracefully(self, *args):
        self.close()
        logging.info(
            'Exiting gracefully')