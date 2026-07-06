from abc import abstractmethod, ABC
from datetime import date

from sqlalchemy import select, func, and_, desc

from database import AsyncSessionLocal
from models import SpimexTradingResult
from filters import filtered_trading_results
from serializers import serialize_trading_results


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
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
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

        return rows

    async def get_trading_results(
            self,
            session: AsyncSessionLocal,
            oil_id: str | None = None,
            delivery_type_id: str | None = None,
            delivery_basis_id: str | None = None,
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

        return rows