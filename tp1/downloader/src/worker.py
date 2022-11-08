import logging

from common.heartbeathed_worker import HeartbeathedWorker
from common.message import EndResult2, MessageEnd, Result2, VideoMessage
from requests import get  # to make GET request

BUFFER_SIZE = 50


class DownloaderInstance(HeartbeathedWorker):
    def __init__(self, middleware, instances) -> None:
        super().__init__(middleware)
        self.instances = instances
        self.done_instances = 0

    def run(self):
        self.middleware.recv_video_message(self.recv_videos)

    def recv_videos(self, message):

        if MessageEnd.is_message(message):
            logging.info(
                f'Finish Recv Videos')
            self.done_instances += 1

            if (self.done_instances == self.instances):
                res = EndResult2()
                self.middleware.send_result_message(res.pack())
                self.done_instances = 0

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
                    file_name, response.content)

        except KeyError:
            logging.error(
                f'Key tags not found in {video.content}')
        except ValueError:
            logging.error(
                f'Incorrect formatted value {video.content}')

    def send_thumbnail(self, file_name, content):
        index = 0
        # print(content)
        while index < len(content):
            next_index = index + BUFFER_SIZE

            if (next_index > len(content)):
                next_index = len(content)

            res = Result2(file_name, content[index:next_index])
            self.middleware.send_result_message(res.pack())

            index = next_index
