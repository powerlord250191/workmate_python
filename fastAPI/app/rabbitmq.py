import logging
from contextlib import asynccontextmanager

from aio_pika import connect_robust

from .config import RMQ_HOST, RMQ_PORT, RMQ_USER, RMQ_PASSWORD

logger = logging.getLogger("RabbitManager logger")


class RabbitMQManager:
    def __init__(self):
        self._connection = None
        self._channel = None

    async def connect(self):
        if self._connection is None or self._connection.is_closed:
            self._connection = await connect_robust(
                host=RMQ_HOST,
                port=RMQ_PORT,
                login=RMQ_USER,
                password=RMQ_PASSWORD,
                virtualhost='/',
                timeout=30,
            )
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=1)
            logger.info("RabbitMQ connected")
        return self._connection, self._channel

    async def close(self):
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        logger.info("RabbitMQ connection closed")

    async def get_channel(self):
        _, channel = await self.connect()
        return channel


def create_rabbit_manager():
    rmq_manager = RabbitMQManager()
    return rmq_manager


@asynccontextmanager
async def get_rabbitmq_channel():
    channel = await create_rabbit_manager().get_channel()
    try:
        yield channel
    finally:
        pass