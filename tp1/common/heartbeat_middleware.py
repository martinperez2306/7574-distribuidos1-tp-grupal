import logging
from common.middleware import Middleware
from multiprocessing import Process
import time

WATCHER_QUEUE = 'watcher_queue'
HEARTBEAT_FRECUENCY = 5 #In seconds

class HeartbeatMiddleware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.reporting = False
        self.channel.queue_declare(
            queue=WATCHER_QUEUE)
        self.channel.basic_qos(prefetch_count=30)
        self.reporting_process: Process = None
        
    def run(self):
        logging.info("HeartbeatMiddleware started")
        self.reporting = True
        self.reporting_process = Process(target=self.report)
        self.reporting_process.start()

    def report(self):
        while self.reporting:
            logging.info("Sending heartbeat")
            super().send_message(WATCHER_QUEUE, "dropper")
            time.sleep(HEARTBEAT_FRECUENCY)

    def send_heartbeat_message(self, message):
        super().send_message(WATCHER_QUEUE, message)

    def stop(self):
        self.reporting = False
        self.reporting_process.join()