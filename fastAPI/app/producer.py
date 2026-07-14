import json
import logging
import aio_pika
from .rabbitmq import create_rabbit_manager
from .config import MQ_ROUTING_KEY

logger = logging.getLogger("Producer logger")
rmq_manager = create_rabbit_manager()


async def publish_message(data: dict, routing_key: str = MQ_ROUTING_KEY) -> bool:
    try:
        channel = await rmq_manager.get_channel()
        queue = await channel.declare_queue(
            routing_key,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        message_body = json.dumps(data, default=str).encode('utf-8')
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type='application/json',
        )

        await channel.default_exchange.publish(
            message,
            routing_key=routing_key,
        )
        logger.info(f"Message published: {data}")
        return True
    except Exception as e:
        logger.error(f"Publish error: {e}", exc_info=True)
        return False