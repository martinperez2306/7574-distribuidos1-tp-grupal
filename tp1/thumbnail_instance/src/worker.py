import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import CategoryMessage, MessageEnd, VideoMessage
from datetime import datetime
from .model import ThumbnailGrouper


class ThumbnailInstance(HeartbeathedWorker):
    def __init__(self, middleware) -> None:
        super().__init__(middleware)
        self.grouper = ThumbnailGrouper()
        self.batch_size = 30        
        self.message_count = 0

    def run(self):
        self.middleware.recv_category_count(self.recv_category_count)
        self.middleware.recv_video_message(self.recv_videos)
        self.middleware.consume()

    def recv_category_count(self, message):
        if CategoryMessage.is_message(message):
            message = CategoryMessage.decode(message)
            client_id = message.client_id

            self.grouper.add_country_count(client_id, int(message.content))

            logging.info(f'Finish Recv Category Count: {message.content}')
                
    def recv_videos(self, message):

        send_ack_flag = False
        self.message_count+=1

        if MessageEnd.is_message(message):
            decoded_message = MessageEnd.decode(message)
            decoded_message.message_id = self.id

            logging.info(f'Finish Thumbnail Grouping Videos for Client: {decoded_message.client_id}')
            self.middleware.send_result_message(decoded_message.pack())
            send_ack_flag = True
            return send_ack_flag
            
        video = VideoMessage.decode(message)
        try:

            video_id = video.content['video_id']
            country = video.content['country']

            trending_date = datetime.strptime(
                video.content['trending_date'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")

            completed = self.grouper.add_date(video.client_id, video_id, country, trending_date)

            if (completed):
                self.middleware.send_result_message(message)
                send_ack_flag = True
                return send_ack_flag

            if (self.batch_size == self.message_count):
                self.grouper.persist_data()
                self.message_count = 0 
                send_ack_flag = True
                                     
            return send_ack_flag

        except KeyError:
            logging.error(f'Key tags not found in {video.content}')
            return False
