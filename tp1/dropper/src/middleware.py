from common.middleware import Middleware
import os

RAW_DATA_EXCHANGE = 'input_exchange'
JOINER_EXCHANGE = 'joiner_exchange'
PREFIX_DROPPER_INPUT_QUEUE = 'dropper_input_'
VIDEO_DATA_QUEUE = 'video_data'


class DropperMiddlware(Middleware):
    def __init__(self, instance_nr) -> None:
        super().__init__()
        self.nr_output_instances = int(os.environ['OUTPUT_INSTANCES'])

        self.dropper_input = PREFIX_DROPPER_INPUT_QUEUE + instance_nr

        self.channel.exchange_declare(exchange=RAW_DATA_EXCHANGE,
                                      exchange_type='direct')
        
        self.channel.exchange_declare(exchange=JOINER_EXCHANGE,
                                      exchange_type='direct')

        self.channel.queue_declare(
            queue=self.dropper_input, durable=True)
        
        # Bind Data messages sent to instance nr
        self.channel.queue_bind(
            exchange=RAW_DATA_EXCHANGE, queue=self.dropper_input, routing_key=instance_nr)
        
        # Bind End message
        self.channel.queue_bind(
            exchange=RAW_DATA_EXCHANGE, queue=self.dropper_input, routing_key='end')

        self.channel.queue_declare(
            queue=VIDEO_DATA_QUEUE, durable=True)
        self.channel.basic_qos(prefetch_count=30)

    def recv_video_message(self, callback):

        self.vid_msg_tag = super().recv_message(self.dropper_input, callback)
        self.channel.start_consuming()


    def send_video_message(self, message, message_id):
        instance_nr = hash(message_id) % self.nr_output_instances
        
        super().send_to_exchange(JOINER_EXCHANGE, str(instance_nr), message)
        

    def send_end_message(self, message):
        super().send_to_exchange(JOINER_EXCHANGE,'end', message)