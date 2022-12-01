import logging
import os
import pika

logging.getLogger("pika").propagate = False


class Middleware():
    def __init__(self) -> None:
        host = os.environ['RABBIT_SERVER_ADDRESS']

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host))

        self.channel = self.connection.channel()

    def send_message(self, queue, message):
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=message)

    def send_to_exchange(self, exchange, routing_key, message):
        self.channel.basic_publish(exchange=exchange,
                                   routing_key=routing_key,
                                   body=message)

    def stop_recv_message(self, consumer_tag):
        self.channel.basic_cancel(consumer_tag=consumer_tag)

    def recv_message(self, queue, callback):
        return self.channel.basic_consume(queue, lambda ch, method,
                                                properties, body: self.callback_with_ack(callback, ch, method, properties, body.decode()), auto_ack=False)
    
    def recv_batch_message(self, queue, callback):
        return self.channel.basic_consume(queue, lambda ch, method, properties, 
                                                body: self.callback_with_multiple_ack(callback, ch, method, properties, body.decode()), auto_ack=False)

    def close_connection(self):
        self.connection.close()

    def consume(self):
        self.channel.start_consuming()

    def callback_with_ack(self, callback, ch, method, properties, body):
        callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback_with_multiple_ack(self, callback, ch, method, properties, body):
        send_ack_flag = callback(body)
        if send_ack_flag:
            ch.basic_ack(delivery_tag=method.delivery_tag, multiple=True)
        