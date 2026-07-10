import asyncio
import json
import logging
import signal
from aio_pika import connect_robust, IncomingMessage

from .config import (
    RMQ_HOST,
    RMQ_PORT,
    RMQ_USER,
    RMQ_PASSWORD,
    MQ_ROUTING_KEY,
)
from .repositories import TradingRepository
from .database import AsyncSessionLocal
from .cache import cache_service

logger = logging.getLogger(f"Consumer {__name__} logger")


def get_trading_repository() -> TradingRepository:
    session_factory = AsyncSessionLocal
    return TradingRepository(session_factory)


async def process_message(message: IncomingMessage) -> None:
    async with message.process(requeue=True):
        try:
            body = message.body.decode('utf-8')
            data = json.loads(body)

            logger.info(f"📨 Received: {data}")

            await handle_trading_data(data)

            logger.info(f"✅ Message processed: {message.delivery_tag}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            raise


async def handle_trading_data(data: dict) -> None:

    if data["router"] == "get_last_trading_dates":
        search_data = data["limit"]
        logger.info(search_data)
        worker = get_trading_repository()
        result = await worker.get_last_trading_dates(search_data)
        logger.info(result)
        return await cache_service.get_or_set("last_trading_dates", search_data, result)


async def consume_messages() -> None:
    try:
        connection = await connect_robust(
            host=RMQ_HOST,
            port=RMQ_PORT,
            login=RMQ_USER,
            password=RMQ_PASSWORD,
            virtualhost='/',
            timeout=30,
        )

        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(
                MQ_ROUTING_KEY,
                durable=True,
                exclusive=False,
                auto_delete=False,
            )

            logger.info(f"👂 Waiting for messages on: {MQ_ROUTING_KEY}")
            logger.info("Press Ctrl+C to stop...")

            await queue.consume(process_message)

            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                logger.info("Consumer cancelled")

    except asyncio.CancelledError:
        logger.info("Consumer stopped")
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)
        raise


async def start_consumer():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task())
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task())

    await consume_messages()


# async def shutdown():
#     logger.info("Shutting down...")
#     for task in asyncio.all_tasks():
#         task.cancel()
