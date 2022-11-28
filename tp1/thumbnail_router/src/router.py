import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import MessageEnd, VideoMessage
from common.end_message_tracker import EndMessageTracker

class ThumbnailRouter(HeartbeathedWorker):
    def __init__(self, middleware, instances, prev_pipeline_instances) -> None:
        super().__init__(middleware)
        self.nr_instances = instances
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
                for id in range(self.nr_instances):
                    logging.info(
                        f'Finish Recv Videos. Forward end message to Thumbnail Instance: {id}')
    
                    self.middleware.send_video_message(parsed_message.pack(), str(id))

            return


        video = VideoMessage.decode(message)

        try:
            if (video.content['video_id'] != None):
                id = str(self.get_instance_n(
                    video.content['video_id']))

                self.middleware.send_video_message(message, id)
        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')

    def get_instance_n(self, key):
        return hash(key) % self.nr_instances
