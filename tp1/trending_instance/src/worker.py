import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import MessageEnd, Result3, VideoMessage
from datetime import datetime
from .model import Grouper


class TrendingInstance(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.grouper = Grouper()

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            end_message = MessageEnd.decode(message)
            client_id = end_message.client_id
            logging.info(
                f'Finish Recv Videos for client: {client_id}. Found {self.grouper.len(client_id)} days')

            self.process_and_send_results(client_id)
            return

        video = VideoMessage.decode(message)

        try:

            if (video.content['trending_date'] != None and video.content['view_count'] != None):
                date = datetime.strptime(
                    video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ')

                views = int(video.content['view_count'])
                client_id = video.client_id
                message_id = video.message_id

                self.grouper.add_value(client_id, message_id, date, views)

        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
        except ValueError:
            logging.error(
                f'Incorrect formatted value {video.content}')

    def process_and_send_results(self, client_id):

        max_date, max_number = self.grouper.get_max(client_id)

        result = Result3(client_id, self.id, f"{max_date},{max_number}")
        self.middleware.send_result_message(result.pack())

        return
