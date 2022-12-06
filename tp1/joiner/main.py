#!/usr/bin/env python
import logging
import os
from src.joiner import Joiner
from src.middleware import JoinerMiddlware


def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'INFO')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Jointer starting work")
    logging.getLogger("pika").setLevel(logging.ERROR)

    prev_pipeline_instances = int(os.getenv("N_PREV_WORKER_INSTANCES"))
    likes_instances = int(os.getenv("LIKES_INSTANCES"))
    thumbnail_router_instances = int(os.getenv("GROUPER_INSTANCES"))

    instance_n = os.getenv("INSTANCE_NR") or '0'
    # Initialize server and start server loop
    middleware = JoinerMiddlware(instance_n, likes_instances, thumbnail_router_instances)
    worker = Joiner(middleware, prev_pipeline_instances)

    worker.start()

    logging.info('Bye bye!')


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
