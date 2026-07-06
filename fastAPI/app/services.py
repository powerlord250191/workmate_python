from datetime import date
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from repositories import ABCTradingRepository
from schemas import TradingResultResponse
from serializers import serialize_trading_results, serialize_trading_dates


class TradingService:
    def __init__(
            self,
            repository: ABCTradingRepository,
            session_factory: Callable[[], AsyncSession],
    ):
        self._repository = repository
        self._session_factory = session_factory

    async def get_last_trading_dates(self, limit: int = 10) -> list[dict]:
        async with self._session_factory() as session:
            data = await self._repository.get_last_trading_dates(session, limit)
            return serialize_trading_dates(data)

    async def get_dynamics(
            self,
            start_date: date,
            end_date: date,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list[TradingResultResponse]:
        async with self._session_factory() as session:
            data = await self._repository.get_dynamics(
                session, start_date, end_date, oil_id, delivery_type_id, delivery_basis_id
            )
            return serialize_trading_results(data)

    async def get_trading_results(
            self,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list[TradingResultResponse]:
        async with self._session_factory() as session:
            data = await self._repository.get_trading_results(
                session, oil_id, delivery_type_id, delivery_basis_id
            )
            return serialize_trading_results(data)
