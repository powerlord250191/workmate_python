from datetime import date
from typing import Callable
from abc import abstractmethod, ABC

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .filters import filtered_trading_results
from .models import SpimexTradingResult
from .schemas import TradingResultResponse
from .serializers import serialize_trading_results, serialize_trading_dates
from .database import AsyncSessionLocal


class ABCTradingRepository(ABC):

    @abstractmethod
    async def get_last_trading_dates(
            self,
            session: AsyncSessionLocal,
            limit: int,
    ) -> list[tuple[date, int]]:
        pass

    @abstractmethod
    async def get_dynamics(
            self,
            session: AsyncSessionLocal,
            start_date: date,
            end_date: date,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list:
        pass

    @abstractmethod
    async def get_trading_results(
            self,
            session: AsyncSessionLocal,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list:
        pass


class TradingRepository(ABCTradingRepository):
    def __init__(
            self,
            session_factory: Callable[[], AsyncSession],
    ):
        self._session_factory = session_factory

    async def get_last_trading_dates(self, limit: int = 10) -> list[dict]:
        async with self._session_factory() as session:
            effective_limit = max(1, limit)
            async with self._session_factory() as session:
                query = (
                    select(
                        SpimexTradingResult.date,
                        func.count(SpimexTradingResult.id).label('total_records')
                    )
                    .group_by(SpimexTradingResult.date)
                    .order_by(desc(SpimexTradingResult.date))
                    .limit(effective_limit)
                )

                result = await session.execute(query)
                rows = result.all()

            data = [
                {
                    "trading_date": row.date,
                    "total_records": row.total_records
                }
                for row in rows
            ]
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
            conditions = [SpimexTradingResult.date >= start_date, SpimexTradingResult.date <= end_date]

            conditions.extend(filtered_trading_results(
                oil_id=oil_id,
                delivery_type_id=delivery_type_id,
                delivery_basis_id=delivery_basis_id)
            )

            query = (
                select(SpimexTradingResult)
                .where(and_(*conditions))
                .order_by(
                    desc(SpimexTradingResult.date),
                    SpimexTradingResult.id
                )
            )

            result = await session.execute(query)
            data = result.scalars().all()
        return serialize_trading_results(data)

    async def get_trading_results(
            self,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
    ) -> list[TradingResultResponse]:
        async with self._session_factory() as session:
            last_date = await session.execute(
                select(func.max(SpimexTradingResult.date))
            )

            last_date = last_date.scalar()

            if last_date is None:
                return []

            conditions = [SpimexTradingResult.date == last_date]

            conditions.extend(filtered_trading_results(
                oil_id=oil_id,
                delivery_type_id=delivery_type_id,
                delivery_basis_id=delivery_basis_id)
            )

            query = (
                select(SpimexTradingResult)
                .where(and_(*conditions))
                .order_by(SpimexTradingResult.id)
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return serialize_trading_results(data)
