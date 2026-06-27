from datetime import datetime
import logging
from typing import Any
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services import TradingService
from schemas import (
    TradingResultResponse,
    TradingDateResponse,
    TradingResultsParams,
    LastTradingDatesParams,
    DynamicsParams,
)
from cache import cache_service


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Spimex Trading API",
    version="1.0.0",
    description="API для работы с данными биржевых торгов"
)

last_cache_reset = None


# ==================== Cache Functions ====================

async def clear_cache_if_needed() -> None:
    """Проверяет и сбрасывает кэш в 14:11"""
    global last_cache_reset
    try:
        now = datetime.now()
        reset_time = datetime.strptime("14:11", "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        if last_cache_reset is None or (now >= reset_time and last_cache_reset < reset_time):
            await cache_service.clear_cache()
            last_cache_reset = now
            logger.info(f"Кэш сброшен в {now.strftime('%H:%M:%S')}")
    except Exception as e:
        logger.warning(f"Ошибка при очистке кэша: {e}")


@app.on_event("startup")
async def startup_event() -> None:
    global last_cache_reset
    try:
        await cache_service.clear_cache()
        last_cache_reset = datetime.now()
        logger.info("Кэш инициализирован")
    except Exception as e:
        logger.warning(f"Ошибка при инициализации кэша: {e}")


@app.get("/", tags=["Root"])
async def root() -> dict[str, str | dict]:
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "status": "OK",
        "service": "Spimex Trading API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "last_trading_dates": "/last_trading_dates?limit=10",
            "dynamics": "/dynamics?start_date=2024-01-01&end_date=2024-01-31&oil_id=100",
            "trading_results": "/trading_results?oil_id=100&delivery_type_id=F"
        }
    }


@app.get("/last_trading_dates", tags=["Trading"])
async def get_last_trading_dates(
        params: LastTradingDatesParams = Depends(),
        db: AsyncSession = Depends(get_db),
) -> list[TradingDateResponse]:

    await clear_cache_if_needed()

    cache_params = {"limit": params.limit}

    async def fetch():
        return await TradingService.get_last_trading_dates(db, params.limit)

    return await cache_service.get_or_set("last_trading_dates", cache_params, fetch)


@app.get("/dynamics", tags=["Trading"])
async def get_dynamics(
        params: DynamicsParams = Depends(),
        db: AsyncSession = Depends(get_db),
) -> list[TradingResultResponse]:

    cache_params = {
        "start_date": str(params.start_date),
        "end_date": str(params.end_date),
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
    }

    async def fetch():
        return await TradingService.get_dynamics(
            db,
            params.start_date,
            params.end_date,
            params.oil_id,
            params.delivery_type_id,
            params.delivery_basis_id
        )

    return await cache_service.get_or_set("dynamics", cache_params, fetch)


@app.get("/trading_results", tags=["Trading"])
async def get_trading_results(
        params: TradingResultsParams = Depends(),
        db: AsyncSession = Depends(get_db)
) -> list[TradingResultResponse]:

    cache_params = {
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
    }

    async def fetch():
        return await TradingService.get_trading_results(
            db,
            params.oil_id,
            params.delivery_type_id,
            params.delivery_basis_id,
        )

    return await cache_service.get_or_set("trading_results", cache_params, fetch)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str | Any]:
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "Spimex Trading API",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/cache/status", tags=["Cache"])
async def cache_status() -> dict[str, str | Any]:
    try:
        await cache_service.redis.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "redis": redis_status,
        "last_cache_reset": last_cache_reset.isoformat() if last_cache_reset else None
    }

