from datetime import date
from typing import Optional

from repositories import ABCTradingRepository
from schemas import TradingResultResponse
from database import AsyncSessionLocal
from serializers import TradingSerializer


class TradingService:
    def __init__(
            self,
            repository: ABCTradingRepository,
            serializer: TradingSerializer,
    ):
        self._repository = repository
        self._serializer = serializer
        self._session_factory = AsyncSessionLocal

    async def get_last_trading_dates(self, limit: int = 10) -> list[dict]:
        async with self._session_factory() as session:
            data = await self._repository.get_last_trading_dates(session, limit)
            return self._serializer.serialize_trading_dates(data)

    async def get_dynamics(
            self,
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[TradingResultResponse]:
        async with self._session_factory() as session:
            data = await self._repository.get_dynamics(
                session, start_date, end_date, oil_id, delivery_type_id, delivery_basis_id
            )
            return self._serializer.serialize_trading_results(data)

    async def get_trading_results(
            self,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[TradingResultResponse]:
        async with self._session_factory() as session:
            data = await self._repository.get_trading_results(
                session, oil_id, delivery_type_id, delivery_basis_id
            )
            return self._serializer.serialize_trading_results(data)
