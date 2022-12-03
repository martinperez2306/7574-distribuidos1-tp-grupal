import logging
from common.middleware import Middleware

WATCHER_EXCHANGE = 'watcher_exchange'

class HeartbeatMiddleware(Middleware):
    def __init__(self, heartbeat_id) -> None:
        super().__init__()
        self.heartbeat_id = heartbeat_id
        self.channel.exchange_declare(
            exchange=WATCHER_EXCHANGE, exchange_type='fanout')
        

    def send_heartbeat(self):
        super().send_to_exchange(WATCHER_EXCHANGE, '', self.heartbeat_id)
