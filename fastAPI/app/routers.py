from datetime import datetime
import logging
from asyncio import sleep, get_running_loop
from fastapi import Depends, Query, APIRouter, HTTPException, status
from .repositories import TradingRepository
from .schemas import (
    TradingResultResponse,
    TradingDateResponse,
    TradingResultsParams,
    LastTradingDatesParams,
    DynamicsParams,
)
from .database import AsyncSessionLocal
from .cache import create_cache
from .producer import publish_message


router = APIRouter()
cache_service = create_cache()
logger = logging.getLogger("Router logger")


def get_trading_repository() -> TradingRepository:
    session_factory = AsyncSessionLocal
    return TradingRepository(session_factory)


async def wait_for_cache_result(
        key: str,
        params: dict,
        timeout: float = 30.0,
        check_interval: float = 0.5
) -> list | None:
    loop = get_running_loop()
    start_time = loop.time()

    while True:
        result = await cache_service.get(key, params)
        if result is not None:
            logger.info(f"Result found in cache after {loop.time() - start_time:.2f}s")
            return result

        if loop.time() - start_time > timeout:
            logger.error(f"Timeout waiting for result in cache ({timeout}s)")
            return None

        await sleep(check_interval)


@router.get("/", tags=["Root"])
async def root() -> dict[str, str | dict[str, str]]:
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


@router.get("/last_trading_dates", tags=["Trading"])
async def get_last_trading_dates(
        params: LastTradingDatesParams = Depends(),
) -> list[TradingDateResponse] | None:

    cache_params = {
        "limit": params.limit,
        "router": "last_trading_dates",
    }

    cached_result = await cache_service.get("last_trading_dates", cache_params)
    if cached_result is not None:
        return cached_result

    await publish_message(data=cache_params)

    result = await wait_for_cache_result("last_trading_dates", cache_params)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Gateway Timeout: Consumer did not respond"
        )

    return result


@router.get("/dynamics", tags=["Trading"])
async def get_dynamics(
        params: DynamicsParams = Depends(),
) -> list[TradingResultResponse]:

    cache_params = {
        "start_date": str(params.start_date),
        "end_date": str(params.end_date),
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
        "router": "dynamics",
    }

    cached_result = await cache_service.get("dynamics", cache_params)

    if cached_result is not None:
        return cached_result

    await publish_message(data=cache_params)

    result = await wait_for_cache_result("dynamics", cache_params)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Gateway Timeout: Consumer did not respond"
        )

    return result


@router.get("/trading_results", tags=["Trading"])
async def get_trading_results(
        params: TradingResultsParams = Depends(),
) -> list[TradingResultResponse]:

    cache_params = {
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
        "router": "trading_results",
    }

    cached_result = await cache_service.get("trading_results", cache_params)

    if cached_result is not None:
        return cached_result

    await publish_message(data=cache_params)

    result = await wait_for_cache_result("dynamics", cache_params)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Gateway Timeout: Consumer did not respond"
        )

    return result


@router.get("/health", tags=["Health"])
async def health_check() -> dict[str, str | datetime]:
    return {
        "status": "healthy",
        "service": "Spimex Trading API",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/cache/status", tags=["Cache"])
async def cache_status() -> dict[str, str | None]:
    try:
        await cache_service.redis.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "redis": redis_status,
        "last_cache_reset": None
    }
