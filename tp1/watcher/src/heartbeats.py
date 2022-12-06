import logging
from datetime import datetime
import os

from common.constants import SERVICE_HEARTBEAT_TIMEOUT

class Heartbeats:
    def __init__(self, config_params) -> None:
        self.hearbeats = dict()
        self._init_hearbeats(config_params)

    def _init_hearbeats(self, config_params):
        joiner_instances = int(config_params['joiner_instances'])
        dropper_instances = int(config_params['dropper_instances'])
        trending_instances = int(config_params['trending_instances'])
        thumbnail_instances = int(config_params['thumbnail_instances'])
        like_filter_instances = int(config_params['like_filter_instances'])
        self.hearbeat("acceptor")
        self.hearbeat("downloader")
        self.hearbeat("tag_unique")
        self.hearbeat("thumbnail_router")
        self.hearbeat("trending_router")
        self.hearbeat("trending_top")
        self._init_service_hearbeats("joiner", joiner_instances)
        self._init_service_hearbeats("dropper", dropper_instances)
        self._init_service_hearbeats("trending", trending_instances)
        self._init_service_hearbeats("thumbnail", thumbnail_instances)
        self._init_service_hearbeats("like_filter", like_filter_instances)

    def _init_service_hearbeats(self, service_name, service_instances):
        for i in range(service_instances):
            service_id = service_name + "_" + str(i)
            self.hearbeat(service_id)

    def hearbeat(self, service_id):
        if service_id:
            self.hearbeats[service_id] = self._get_current_timestamp()

    def get_unavailable_services(self) -> list:
        unavailable_services = list()
        for service_id in self.hearbeats:
            current_timestamp = self._get_current_timestamp()
            service_last_timestamp = self.hearbeats.get(service_id)
            timeout_timestamp = SERVICE_HEARTBEAT_TIMEOUT + service_last_timestamp
            logging.debug("Current Timestamp [{}]. Service Timeout Timestamp [{}]".format(current_timestamp, timeout_timestamp))
            if current_timestamp > timeout_timestamp:
                logging.info("Service [{}] is unavailable".format(service_id))
                unavailable_services.append(service_id)
        for unavailable_service in unavailable_services:
            self.hearbeats.pop(unavailable_service)
        return unavailable_services

    def _get_current_timestamp(self) -> float:
        # Getting the current date and time
        dt = datetime.now()
        # getting the timestamp
        timestamp = datetime.timestamp(dt)
        return timestamp