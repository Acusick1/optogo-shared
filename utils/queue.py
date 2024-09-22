import logging
import ssl
from typing import Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel

from packages.config import settings

LOGGER = logging.getLogger(__name__)


def open_pika_connection(url: str = settings.cloudamqp_url):
    LOGGER.info(f"Opening pika connection to: {url.split('@')[-1]}")

    if "amazonaws" in url:
        # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")

        params = pika.URLParameters(url)
        params.ssl_options = pika.SSLOptions(context=ssl_context)
    else:
        params = pika.URLParameters(url)

    return pika.BlockingConnection(params)


def consume(
    queue: str, callback: Callable, url: str = settings.cloudamqp_url, prefetch: int = 1
):
    while True:
        try:
            connection = open_pika_connection(url)
            channel = connection.channel()  # Start channel
            channel.basic_qos(
                prefetch_count=prefetch
            )  # Avoids backlog by only sending one message at a time to each consumer
            channel.queue_declare(queue=queue, durable=True)  # Declare queue
            channel.basic_consume(queue, callback)

            print("Waiting for messages...")
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
        exchange="",
        routing_key=queue,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
        body=body,
    )
