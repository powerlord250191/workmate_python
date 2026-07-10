import asyncio
import json
import logging

import aio_pika
from aio_pika import connect_robust, Message

from .config import (
    RMQ_HOST,
    RMQ_PORT,
    RMQ_USER,
    RMQ_PASSWORD,
    MQ_ROUTING_KEY,
)


logger = logging.getLogger("Producer logger")


async def get_connection() -> aio_pika.RobustConnection:
    return await connect_robust(
        host=RMQ_HOST,
        port=RMQ_PORT,
        login=RMQ_USER,
        password=RMQ_PASSWORD,
        virtualhost='/',
        timeout=30,
    )


async def get_channel() -> aio_pika.Channel:
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    return channel


async def publish_message(data: dict, routing_key: str = MQ_ROUTING_KEY) -> bool:

    try:
        connection = await get_connection()
        async with connection:
            channel = await connection.channel()

            queue = await channel.declare_queue(
                routing_key,
                durable=True,
                exclusive=False,
                auto_delete=False,
            )

            message_body = json.dumps(data, default=str).encode('utf-8')
            message = Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type='application/json',
                headers={'timestamp': str(asyncio.get_event_loop().time())},
            )

            await channel.default_exchange.publish(
                message,
                routing_key=routing_key,
            )

            logger.info(f"✅ Message published: {data}")
            return True

    except Exception as e:
        logger.error(f"❌ Publish error: {e}", exc_info=True)
        return False


async def publish_many(messages: list[dict]) -> None:
    tasks = [publish_message(msg) for msg in messages]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"❌ Message {i} failed: {result}")
        else:
            logger.info(f"✅ Message {i} sent")