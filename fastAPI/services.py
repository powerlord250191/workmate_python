from datetime import date
from typing import Optional
from abc import abstractmethod, ABC
from sqlalchemy import select, func, and_, desc

from models import SpimexTradingResult
from schemas import TradingResultResponse
from database import AsyncSessionLocal


class ABCTrading(ABC):

    @abstractmethod
    async def get_last_trading_dates(
            self,
            session: AsyncSessionLocal,
            limit: int,
    ) -> list:
        pass

    @abstractmethod
    async def get_dynamics(
            self,
            session: AsyncSessionLocal,
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list:
        pass

    @abstractmethod
    async def get_trading_results(
            self,
            session: AsyncSessionLocal,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list:
        pass


def filtered_trading_results(
        oil_id: Optional[str] = None,
        delivery_type_id: Optional[str] = None,
        delivery_basis_id: Optional[str] = None,
) -> list:

    conditions = []

    if oil_id:
        conditions.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    return conditions


class TradingSerializer:

    @staticmethod
    def serialize_trading_results(rows: list[SpimexTradingResult]) -> list[TradingResultResponse]:
        return [
            TradingResultResponse.model_validate(row).model_dump()
            for row in rows if row
        ]

    @staticmethod
    def serialize_trading_dates(rows: list[dict]) -> list[dict]:
        return rows


class TradingRepository(ABCTrading):

    async def get_last_trading_dates(
            self,
            session: AsyncSessionLocal,
            limit: int,
    ) -> list[dict[str, str]]:
        effective_limit = max(1, limit)
        async with session as session:
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

        return [
            {
                "trading_date": row.date,
                "total_records": row.total_records
            }
            for row in rows
        ]

    async def get_dynamics(
            self,
            session: AsyncSessionLocal,
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[dict[str, str]]:
        conditions = [SpimexTradingResult.date >= start_date, SpimexTradingResult.date <= end_date]

        conditions.extend(filtered_trading_results(
            oil_id=oil_id,
            delivery_type_id=delivery_type_id,
            delivery_basis_id=delivery_basis_id)
        )

        async with session as session:
            query = (
                select(SpimexTradingResult)
                .where(and_(*conditions))
                .order_by(
                    desc(SpimexTradingResult.date),
                    SpimexTradingResult.id
                )
            )

            result = await session.execute(query)
            rows = result.scalars().all()

        return TradingSerializer().serialize_trading_results(rows)

    async def get_trading_results(
            self,
            session: AsyncSessionLocal,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[dict[str, str]]:

        async with session as session:
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
            rows = result.scalars().all()

        return TradingSerializer.serialize_trading_results(rows)


class TradingService:
    def __init__(
            self,
            repository: ABCTrading,
            serializer: TradingSerializer = None,
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
