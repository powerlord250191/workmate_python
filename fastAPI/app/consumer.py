import asyncio
import json
import logging
from datetime import datetime
from aio_pika import IncomingMessage
from .rabbitmq import create_rabbit_manager
from .repositories import TradingRepository
from .database import AsyncSessionLocal
from .cache import create_cache
from .config import MQ_ROUTING_KEY


logger = logging.getLogger(__name__)
rmq_manager = create_rabbit_manager()
cache_service = create_cache()

_consumer_task = None
_stop_event = asyncio.Event()


def get_trading_repository():
    return TradingRepository(AsyncSessionLocal)


def current_date(start_date_str, end_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return start_date, end_date
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")


async def write_to_cache(
        key: str,
        cache_params: dict,
        result: list
        ):
    await cache_service.set(key, cache_params, result)
    logger.info(f"Cached result for data={cache_params}")


async def process_message(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        try:
            body = message.body.decode('utf-8')
            data = json.loads(body)
            logger.info(f"Received: {data}")

            await handle_trading_data(data)

            logger.info(f"Message processed: {message.delivery_tag}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)


async def handle_trading_data(data: dict) -> None:

    key = data.get("router")

    if key == "last_trading_dates":
        limit = data.get("limit")
        if limit is None:
            logger.error("Missing 'limit' in message")
            return
        repo = get_trading_repository()
        result = await repo.get_last_trading_dates(limit)
        cache_params = {
            "limit": limit,
            "router": "last_trading_dates",
        }

    elif key == "dynamics":
        repo = get_trading_repository()
        start_date, end_date = current_date(data.get("start_date"), data.get("end_date"))

        result = await repo.get_dynamics(
            oil_id=data.get("oil_id"),
            delivery_type_id=data.get("delivery_type_id"),
            delivery_basis_id=data.get("delivery_basis_id"),
            start_date=start_date,
            end_date=end_date,
        )

        cache_params = {
            "start_date": str(data.get("start_date")),
            "end_date": str(data.get("end_date")),
            "oil_id": data.get("oil_id"),
            "delivery_type_id": data.get("delivery_type_id"),
            "delivery_basis_id": data.get("delivery_basis_id"),
            "router": "dynamics",
        }

    elif key == "trading_results":
        repo = get_trading_repository()

        result = await repo.get_trading_results(
            oil_id=data.get("oil_id"),
            delivery_type_id=data.get("delivery_type_id"),
            delivery_basis_id=data.get("delivery_basis_id"),
        )
        cache_params = {
            "oil_id": data.get("oil_id"),
            "delivery_type_id": data.get("delivery_type_id"),
            "delivery_basis_id": data.get("delivery_basis_id"),
            "router": "trading_results",
        }

    await write_to_cache(
        key=key,
        cache_params=cache_params,
        result=result
    )


async def start_consumer():
    logger.info("start_consumer called")
    try:
        await rmq_manager.connect()
        channel = await rmq_manager.get_channel()
        queue = await channel.declare_queue(MQ_ROUTING_KEY, durable=True)
        logger.info(f"Listening on queue: {MQ_ROUTING_KEY}")
        await queue.consume(process_message)
        await _stop_event.wait()
    except asyncio.CancelledError:
        logger.info("Consumer cancelled")
        raise
    except Exception as e:
        logger.error(f"Consumer error: {e}", exc_info=True)
        raise


async def shutdown_consumer():
    _stop_event.set()
    await rmq_manager.close()
    logger.info("Consumer shutdown initiated")