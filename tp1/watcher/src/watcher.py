import logging
import os
import pika

WATCHER_QUEUE = "watcher_queue"

class Watcher:
    def __init__(self) -> None:
        self.connection = None
        self.channel = None
        self.tries = 0

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
                self.tries+=1

            else:
                # Display the message parts
                print(method_frame)
                print(properties)
                print(body)

                # Acknowledge the message
                self.channel.basic_ack(method_frame.delivery_tag)

            # Escape out of the loop after N tries
            if self.tries == 100:
                break

        # Cancel the consumer and return any pending messages
        requeued_messages = self.channel.cancel()
        print('Requeued %i messages' % requeued_messages)

        # Close the channel and the connection
        self.channel.close()
        self.connection.close()