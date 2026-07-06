from datetime import datetime
from typing import Annotated
from fastapi import Depends, Query, APIRouter
from services import TradingService
from schemas import (
    TradingResultResponse,
    TradingDateResponse,
    TradingResultsParams,
    LastTradingDatesParams,
    DynamicsParams,
)
from database import AsyncSessionLocal
from repositories import TradingRepository
from cache import cache_service

router = APIRouter()


def get_trading_service() -> TradingService:
    repository = TradingRepository()
    session_factory = AsyncSessionLocal
    return TradingService(repository, session_factory)


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
        params: Annotated[LastTradingDatesParams, Query()],
        service: TradingService = Depends(get_trading_service),
) -> list[TradingDateResponse]:

    cache_params = {"limit": params.limit}

    result = await service.get_last_trading_dates(params.limit)
    return await cache_service.get_or_set("last_trading_dates", cache_params, result)


@router.get("/dynamics", tags=["Trading"])
async def get_dynamics(
        params: DynamicsParams = Depends(),
        service: TradingService = Depends(get_trading_service),
) -> list[TradingResultResponse]:

    cache_params = {
        "start_date": str(params.start_date),
        "end_date": str(params.end_date),
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
    }

    result = await service.get_dynamics(
        oil_id=params.oil_id,
        delivery_type_id=params.delivery_type_id,
        delivery_basis_id=params.delivery_basis_id,
        start_date=params.start_date,
        end_date=params.end_date,
    )

    return await cache_service.get_or_set("dynamics", cache_params, result)


@router.get("/trading_results", tags=["Trading"])
async def get_trading_results(
        params: TradingResultsParams = Depends(),
        service: TradingService = Depends(get_trading_service),
) -> list[TradingResultResponse]:

    cache_params = {
        "oil_id": params.oil_id,
        "delivery_type_id": params.delivery_type_id,
        "delivery_basis_id": params.delivery_basis_id,
    }

    result = await service.get_trading_results(
        oil_id=params.oil_id,
        delivery_type_id=params.delivery_type_id,
        delivery_basis_id=params.delivery_basis_id,
    )

    return await cache_service.get_or_set("trading_results", cache_params, result)


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