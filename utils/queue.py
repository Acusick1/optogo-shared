import logging
import pika
import ssl
from pika.adapters.blocking_connection import BlockingChannel
from typing import Callable
from config import settings

LOGGER = logging.getLogger(__name__)


def open_pika_connection(url: str = settings.cloudamqp_url):

    LOGGER.info("Opening pika connection")
    
    try:
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)

    except Exception as e:

        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')

        parameters = pika.URLParameters(url)
        parameters.ssl_options = pika.SSLOptions(context=ssl_context)

        connection = pika.BlockingConnection(parameters)

    return connection



def consume(queue: str, callback: Callable, url: str = settings.cloudamqp_url, prefetch: int = 1):

    while True:
        try:
            connection = open_pika_connection(url)
            channel = connection.channel()  # Start channel
            channel.basic_qos(prefetch_count=prefetch)  # Avoids backlog by only sending one message at a time to each consumer
            channel.queue_declare(queue=queue, durable=True)  # Declare queue
            channel.basic_consume(queue, callback)

            print('Waiting for messages...')
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                channel.stop_consuming()
            finally:
                channel.close()  # `Close channel
                connection.close()  # Close connection

        except Exception as e:
            LOGGER.exception(f"Error when trying to consume queue {queue}: {e}")
            continue


def publish(channel: BlockingChannel, queue: str, body):

    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        body=body
    )
