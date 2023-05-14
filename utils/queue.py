import pika
from pika.adapters.blocking_connection import BlockingChannel
from typing import Callable
from config import settings


def consume(queue: str, callback: Callable, url: str = settings.cloudamqp_url, prefetch: int = 1):

    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()  # Start channel
    channel.basic_qos(prefetch_count=prefetch)  # Avoids backlog by only sending one message at a time to each consumer
    channel.queue_declare(queue=queue, durable=True)  # Declare queue
    channel.basic_consume(queue, callback)

    print('Waiting for messages...')
    try:
        channel.start_consuming()
    except Exception as e:
        print("Exception occurred, closing connection")
        connection.close()
        raise e


def publish(channel: BlockingChannel, queue: str, body):

    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        body=body
    )
