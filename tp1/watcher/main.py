#!/usr/bin/env python
import os
import logging
from configparser import ConfigParser

from src.config import DEFAULT_CONFIG
from src.watcher import Watcher

CONFIG_PATH = "./config/config.ini"

def main():
    config_params = initialize_config(CONFIG_PATH)
    initialize_log(config_params["logging_level"])
    
    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug("Watcher configuration: {}".format(config_params))
    logging.info("Watcher starting work")
    logging.getLogger("pika").setLevel(logging.ERROR)

    # Initialize Watcher and application loops
    watcher = Watcher(config_params)
    watcher.start()
    
    logging.info('Bye bye!')

def initialize_config(config_path):
    config_params = {}
    config = ConfigParser(os.environ)
    for env_key in config["DEFAULT"]:  
        config_params[env_key] = config["DEFAULT"][env_key]
    # If config.ini does not exists original config object is not modified
    config.read(config_path)
    for default_key in DEFAULT_CONFIG: 
        try:
            config_params[default_key] = config["DEFAULT"][default_key]
        except KeyError as e:
            config_params[default_key] = DEFAULT_CONFIG[default_key]
        except ValueError as e:
            raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
    return config_params

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