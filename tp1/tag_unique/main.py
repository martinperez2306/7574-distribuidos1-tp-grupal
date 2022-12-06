#!/usr/bin/env python
import logging
import os
from src.middleware import TagUniqueMiddlware
from src.tag_unique import TagUnique


def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'INFO')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Tag Filter and Unique starting work")
    logging.getLogger("pika").setLevel(logging.ERROR)
    prev_pipeline_instances = int(os.getenv("N_PREV_WORKER_INSTANCES"))
    
    # Initialize server and start server loop
    middleware = TagUniqueMiddlware()
    worker = TagUnique(middleware, prev_pipeline_instances)

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
