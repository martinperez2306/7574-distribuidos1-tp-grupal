import logging
import os
import signal
import pika
import docker

from src.heartbeats import Heartbeats
from src.middleware import WatcherMiddlware

WATCHER_QUEUE = "watcher_queue"

class Watcher:
    def __init__(self) -> None:
        self.heartbeats = Heartbeats()
        self.docker = docker.from_env()
        self.id = os.environ['HOSTNAME']
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        self.middleware = WatcherMiddlware(self.id)

    def start(self):
        self.middleware.accept_heartbeats(self.handle_heartbeat)
        self.middleware.stop()

    def handle_heartbeat(self, heartbeat):
        self.heartbeats.hearbeat(heartbeat)
        unavailable_services = self.heartbeats.get_unavailable_services()
        self.wake_up_services(unavailable_services)

    def wake_up_services(self, unavailable_services: list):
        for service in unavailable_services:
            self.docker.api.stop(service)
            self.docker.api.start(service)
    
    def exit_gracefully(self, *args):
        self.middleware.stop()
        logging.info(
            'Exiting gracefully')