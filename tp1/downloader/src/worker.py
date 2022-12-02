import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult2, MessageEnd, Result2, VideoMessage, BinaryFile
from requests import get  # to make GET request
from .model import EndResultsRepository

BUFFER_SIZE = 50


class DownloaderInstance(HeartbeathedWorker):
    def __init__(self, middleware, instances) -> None:
        super().__init__(middleware)
        self.instances = instances
        self.end_results = EndResultsRepository()
        

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            parsed_message = MessageEnd.decode(message)
            client_id = parsed_message.client_id
            instance_id = parsed_message.message_id

            logging.info(
                f'Finish Recv Videos from Instance: {instance_id} and Client: {client_id}')
            
            self.end_results.add_end_result(client_id, instance_id)
            
            if (self.end_results.len_responses(client_id) == self.instances):
                logging.info(
                f'Finish Recv Videos from all instances. Client: {client_id}')
                res = EndResult2(parsed_message.client_id)
                self.middleware.send_result_message(res.pack())
                
            return

        video = VideoMessage.decode(message)

        try:
            url = video.content['thumbnail_link']
            video_id = video.content['video_id']
            if (url):
                response = get(url)
                file = url.rsplit('/', 1)[-1]

                file_name = f'{video_id}_{file}'
                self.send_thumbnail(
                    video.client_id, file_name, response.content)

        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
        except ValueError:
            logging.error(
                f'Incorrect formatted value {video.content}')
    

    def send_thumbnail(self, client_id, file_name, content):
        index = 0
        # print(content)
        while index < len(content):
            next_index = index + BUFFER_SIZE

            if (next_index > len(content)):
                next_index = len(content)

            msg_content = BinaryFile(
                file_name, content[index:next_index])
            message_id = file_name + '#' + str(index)
            
            res = Result2(client_id, message_id, msg_content.pack())
            self.middleware.send_result_message(res.pack())

            index = next_index
