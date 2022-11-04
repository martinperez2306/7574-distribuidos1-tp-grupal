import logging
import os
import signal
import pika
import docker

from src.heartbeats import Heartbeats

WATCHER_QUEUE = "watcher_queue"

class Watcher:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None
        self.tries = 0
        self.heartbeats = Heartbeats()
        self.docker = docker.from_env()
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
                self.heartbeats.hearbeat(body.decode())
                # Acknowledge the message
                self.channel.basic_ack(method_frame.delivery_tag)

            unavailable_services = self.heartbeats.get_unavailable_services()
            self.wake_up_services(unavailable_services)

        self.close()

    def wake_up_services(self, unavailable_services: list):
        for service in unavailable_services:
            self.docker.api.stop(service)
            self.docker.api.start(service)
    
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