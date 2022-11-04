from datetime import datetime
import logging

SERVICE_TIMEOUT_MILIS = 10000

class Heartbeats:
    def __init__(self) -> None:
        self.hearbeats = dict()

    def hearbeat(self, service_id):
        if service_id:
            self.hearbeats[service_id] = self._get_current_timestamp()

    def check_services(self) -> list:
        for service_id in self.hearbeats:
            logging.info(service_id)
            current_timestamp = self._get_current_timestamp()
            service_last_timestamp = self.hearbeats.get(service_id)
            timeout_timestamp = SERVICE_TIMEOUT_MILIS + service_last_timestamp
            if current_timestamp > timeout_timestamp:
                logging.info("Service [{}] is unavailable".format(service_id))
        return list()

    def _get_current_timestamp(self) -> float:
        # Getting the current date and time
        dt = datetime.now()
        # getting the timestamp
        timestamp = datetime.timestamp(dt)
        return timestamp