from datetime import date
from typing import Optional, Any
from sqlalchemy import select, func, and_, desc

from models import SpimexTradingResult
from schemas import TradingResultResponse
from database import AsyncSessionLocal


class TradingService:

    def __init__(self):
        self.session = AsyncSessionLocal

    async def get_last_trading_dates(self,
                                     limit: int = 10
                                     ) -> list[dict[str, str | None]]:
        effective_limit = max(1, limit)
        async with self.session() as session:
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
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[TradingResultResponse]:

        conditions = TradingService()._build_dynamics_conditions(
            start_date, end_date, oil_id, delivery_type_id, delivery_basis_id
        )

        async with self.session() as session:
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

        return TradingService._serialize_results(rows)

    async def get_trading_results(
            self,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None
    ) -> list[TradingResultResponse]:

        async with self.session() as session:
            last_date = await TradingService()._get_last_trading_date()

            if last_date is None:
                return []

            conditions = TradingService()._build_results_conditions(
                last_date, oil_id, delivery_type_id, delivery_basis_id
            )

            query = (
                select(SpimexTradingResult)
                .where(and_(*conditions))
                .order_by(SpimexTradingResult.id)
            )

            result = await session.execute(query)
            rows = result.scalars().all()

        return TradingService._serialize_results(rows)

    def _build_dynamics_conditions(
            self,
            start_date: date,
            end_date: date,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> list:

        conditions = [
            SpimexTradingResult.date >= start_date,
            SpimexTradingResult.date <= end_date
        ]

        conditions.extend(
            TradingService()._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    def _build_results_conditions(
            self,
            last_date: date,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> list:
        conditions = [SpimexTradingResult.date == last_date]

        conditions.extend(
            TradingService()._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    def _build_optional_filters(
            self,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> list:
        conditions = []

        if oil_id:
            conditions.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id:
            conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        return conditions

    async def _get_last_trading_date(self) -> Optional[date]:
        async with self.session() as session:
            result = await session.execute(
                select(func.max(SpimexTradingResult.date))
            )
            return result.scalar()

    @staticmethod
    def _serialize_results(rows: list[SpimexTradingResult]) -> list:

        if not rows:
            return []

        return [
            TradingResultResponse.model_validate(row).model_dump()
            for row in rows if row
        ]
