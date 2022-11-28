import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import MessageEnd, VideoMessage
from common.end_message_tracker import EndMessageTracker

class LikesFilter(HeartbeathedWorker):
    def __init__(self, middleware, filter_qty, prev_pipeline_instances) -> None:
        super().__init__(middleware)
        self.filter_qty = filter_qty
        self.end_message_tracker = EndMessageTracker(prev_pipeline_instances)

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            parsed_message = MessageEnd.decode(message)
            
            logging.info(
                    f'Recv end message from {parsed_message.client_id} and Instance: {parsed_message.message_id}')
            
            self.end_message_tracker.add_end_message(parsed_message.client_id, parsed_message.message_id)
            parsed_message.message_id = self.id
            if(self.end_message_tracker.is_finished(parsed_message.client_id)):
                logging.info(
                    f'Finish Recv Videos')
                self.middleware.send_video_message(parsed_message.pack())

            return

        video = VideoMessage.decode(message)

        try:
            if (video.content['likes'] != None and int(video.content['likes']) >= self.filter_qty):
                logging.debug(f"Found video that matches {video.content}")
                self.middleware.send_video_message(message)
        except KeyError:
            logging.error(
                f'Key likes not found in {message.content}')
        except ValueError:
            logging.error(
                f'Data not formatted correctly {message.content}')
