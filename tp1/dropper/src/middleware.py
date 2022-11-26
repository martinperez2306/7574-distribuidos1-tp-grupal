from common.middleware import Middleware

DROPPER_INPUT_QUEUE = 'dropper_input'
VIDEO_DATA_QUEUE = 'video_data'


class DropperMiddlware(Middleware):
    def __init__(self) -> None:
        super().__init__()
        self.channel.queue_declare(
            queue=DROPPER_INPUT_QUEUE, durable=True)

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE, durable=True)
        self.channel.basic_qos(prefetch_count=30)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(DROPPER_INPUT_QUEUE, callback)
        self.channel.start_consuming()


    def send_video_message(self, message):
        super().send_message(VIDEO_DATA_QUEUE, message)
