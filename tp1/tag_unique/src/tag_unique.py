import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult1, MessageEnd, Result1, VideoMessage
from common.end_message_tracker import EndMessageTracker
from .model import ResultRepository

class TagUnique(HeartbeathedWorker):
    def __init__(self, middleware, prev_pipeline_instances) -> None:
        super().__init__(middleware)
        self.repository = ResultRepository()
        self.end_message_tracker = EndMessageTracker(prev_pipeline_instances)

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

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
                end_message = EndResult1(parsed_message.client_id)
                self.middleware.send_result_message(end_message.pack())

            return

        video = VideoMessage.decode(message)
        client_id = video.client_id
        try:
            tags = video.content['tags']
            # print(f'Is funny: {'funny' in tags}')
            item = (video.content['video_id'],
                    video.content['title'], video.content['category'])

            if (tags != None and 'funny' in tags and not self.repository.check_element(client_id, item)):
                end_message = Result1(video.client_id, video.message_id, ",".join(item))
                self.middleware.send_result_message(end_message.pack())
                self.repository.add_element(client_id, item, True)

                
        except KeyError:
            logging.error(f'Key tags not found in {video.content}')
