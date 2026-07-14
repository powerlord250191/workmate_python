import logging
import asyncio
from fastapi import FastAPI
from .app_factory import create_app
from .config import configure_logging
from contextlib import asynccontextmanager
from .consumer import start_consumer, shutdown_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    num_consumers = 20
    logger.info("Lifespan started")
    consumer_tasks = [asyncio.create_task(start_consumer()) for _ in range(num_consumers)]
    logger.info(f"Consumers {num_consumers} started")
    yield
    await shutdown_consumer()
    for task in consumer_tasks:
        task.cancel()
    try:
        await asyncio.gather(*consumer_tasks, return_exceptions=True)
    except asyncio.CancelledError:
        pass
    logger.info("Consumer stopped")

logger = logging.getLogger(__name__)


configure_logging(level=logging.INFO)
app = create_app(lifespan=lifespan)
# Тимур красавчик <3