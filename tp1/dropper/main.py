#!/usr/bin/env python
import logging
import os
from src.dropper import Dropper
from src.middleware import DropperMiddlware


def main():

    initialize_log(os.getenv("LOGGING_LEVEL") or 'INFO')

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info("Dropper starting work")

    instance_n = os.getenv("INSTANCE_NR") or '0'

    # Initialize server and start server loop
    middleware = DropperMiddlware(instance_n)
    worker = Dropper(middleware)

    worker.start()

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
