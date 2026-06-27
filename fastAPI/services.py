from datetime import date
from typing import Optional, Any
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import SpimexTradingResult
from schemas import TradingResultResponse


class TradingService:

    async def get_last_trading_dates(
            db: AsyncSession,
            limit: int = 10
    ) -> list[dict[str, Any]]:
        effective_limit = max(1, limit)

        query = (
            select(
                SpimexTradingResult.date,
                func.count(SpimexTradingResult.id).label('total_records')
            )
            .group_by(SpimexTradingResult.date)
            .order_by(desc(SpimexTradingResult.date))
            .limit(effective_limit)
        )

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                "trading_date": row.date,
                "total_records": row.total_records
            }
            for row in rows
        ]

    async def get_dynamics(
            db: AsyncSession,
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> list[dict[str, Any]]:

        conditions = TradingService._build_dynamics_conditions(
            start_date, end_date, oil_id, delivery_type_id, delivery_basis_id
        )

        query = (
            select(SpimexTradingResult)
            .where(and_(*conditions))
            .order_by(
                desc(SpimexTradingResult.date),
                SpimexTradingResult.id
            )
        )

        result = await db.execute(query)
        rows = result.scalars().all()

        return TradingService._serialize_results(rows)

    async def get_trading_results(
            db: AsyncSession,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None
    ) -> list[dict[str, Any]]:

        last_date = await TradingService._get_last_trading_date(db)

        if last_date is None:
            return []

        conditions = TradingService._build_results_conditions(
            last_date, oil_id, delivery_type_id, delivery_basis_id
        )

        query = (
            select(SpimexTradingResult)
            .where(and_(*conditions))
            .order_by(SpimexTradingResult.id)
        )

        result = await db.execute(query)
        rows = result.scalars().all()

        return TradingService._serialize_results(rows)

    # ==================== Приватные вспомогательные методы ====================

    def _build_dynamics_conditions(
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

        # Добавляем опциональные фильтры
        conditions.extend(
            TradingService._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    def _build_results_conditions(
            last_date: date,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> list:
        conditions = [SpimexTradingResult.date == last_date]

        conditions.extend(
            TradingService._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    def _build_optional_filters(
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

    async def _get_last_trading_date(db: AsyncSession) -> Optional[date]:

        result = await db.execute(
            select(func.max(SpimexTradingResult.date))
        )
        return result.scalar()

    def _serialize_results(rows: list[SpimexTradingResult]) -> list[dict[str, Any]]:

        return [
            TradingResultResponse.model_validate(row).model_dump()
            for row in rows
        ]