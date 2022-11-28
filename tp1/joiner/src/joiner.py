import logging
from common.heartbeathed_worker import HeartbeathedWorker
from common.message import CategoryMessage, FileMessage, MessageEnd, VideoMessage, BaseMessage
from src.model import CategoryMapper
from common.end_message_tracker import EndMessageTracker

class Joiner(HeartbeathedWorker):
    def __init__(self, middleware, prev_pipeline_instances: int) -> None:
        super().__init__(middleware)

        self.categories = CategoryMapper()
        self.end_message_tracker = EndMessageTracker(prev_pipeline_instances)

    def run(self):
        self.middleware.recv_category_message(self.recv_categories)
        self.middleware.recv_video_message(self.recv_videos)
        self.middleware.consume()

    def recv_categories(self, message):
        logging.info('New category message')

        if MessageEnd.is_message(message):
            parsed_message = MessageEnd.decode(message)
            logging.info(
                f'Finish Recv Categories, recv {self.categories.len(parsed_message.client_id)} countries for {parsed_message.client_id}')
            message = CategoryMessage(parsed_message.client_id, self.categories.len(parsed_message.client_id))
            self.middleware.send_category_count(message.pack())

            return

        if not FileMessage.is_message(message):
            logging.error(f'Unknown message: {message}')
            return

        file_message = FileMessage.decode(message)

        self.categories.load_category_file(file_message.client_id, 
            file_message.file_name, file_message.file_content)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):

            parsed_message = MessageEnd.decode(message)
            logging.info(
                    f'Recv end message from {parsed_message.client_id} and Instance: {parsed_message.message_id}')
            self.end_message_tracker.add_end_message(parsed_message.client_id, parsed_message.message_id)
            
            if(self.end_message_tracker.is_finished(parsed_message.client_id)):
                parsed_message.message_id = self.id
                logging.info(
                    f'Finish Recv Videos for {parsed_message.client_id}')
                self.middleware.send_video_message(parsed_message.pack())

            return

        video = VideoMessage.decode(message)

        try:
            category_name = self.categories.map_category(video.client_id, 
                video.content['country'], video.content['categoryId'])
            video.content.pop('categoryId')
            video.content['category'] = category_name
            self.middleware.send_video_message(video.pack())
        except KeyError as err:
            logging.debug(f'Invalid key error: {err}')

