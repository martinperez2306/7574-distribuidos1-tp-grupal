#!/usr/bin/env python
import logging
import os
import pika

WATCHER_QUEUE = "watcher_queue"

def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'INFO')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Watcher starting work")

    # Initialize server and start server loop
    host = os.environ['RABBIT_SERVER_ADDRESS']

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host))

    channel = connection.channel()

    channel.queue_declare(
            queue=WATCHER_QUEUE)

    tries = 0

    # Get ten messages and break out
    for method_frame, properties, body in channel.consume(queue=WATCHER_QUEUE, inactivity_timeout=10):

        if method_frame is None and properties is None and body is None:
            logging.info("Timeout for receive message")
            tries+=1

        else:
            # Display the message parts
            print(method_frame)
            print(properties)
            print(body)

            # Acknowledge the message
            channel.basic_ack(method_frame.delivery_tag)

        # Escape out of the loop after 10 tries
        if tries == 10:
            break

    # Cancel the consumer and return any pending messages
    requeued_messages = channel.cancel()
    print('Requeued %i messages' % requeued_messages)

    # Close the channel and the connection
    channel.close()
    connection.close()

    logging.info(
        'Bye bye!')


def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()