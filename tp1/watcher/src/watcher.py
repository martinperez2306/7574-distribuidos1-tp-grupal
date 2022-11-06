import logging
import signal
import docker

from src.heartbeats import Heartbeats
from src.middleware import WatcherMiddlware
from src.hierarchy_worker import HierarchyWorker

WATCHER_QUEUE = "watcher_queue"
WATCHER_HIERARCHY_QUEUE = "watcher_hierarchy_queue"


class Watcher(HierarchyWorker):
    def __init__(self) -> None:
        super().__init__()
        self.heartbeats = Heartbeats()
        self.docker = docker.from_env()
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        self.watcher_middleware = WatcherMiddlware(self.id)

    def start(self):
        logging.info('Starting Watcher')
        super().start()
        self.watcher_middleware.accept_heartbeats(self.handle_heartbeat)
        self.watcher_middleware.stop()

    def handle_heartbeat(self, heartbeat):
        logging.info('Handling hearbeat [{}]'.format(heartbeat))
        self.heartbeats.hearbeat(heartbeat)
        unavailable_services = self.heartbeats.get_unavailable_services()
        self.wake_up_services(unavailable_services)

    def wake_up_services(self, unavailable_services: list):
        logging.info('Waking up services[{}]')
        if self.im_master():
            for service in unavailable_services:
                logging.debug("Starting unavailable service [{}]".format(service))
                self.docker.api.stop(service)
                self.docker.api.start(service)
    
    def exit_gracefully(self, *args):
        self.watcher_middleware.stop()
        logging.info('Exiting gracefully')