from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models import SpimexTradingResult
from schemas import TradingResultResponse


class TradingService:
    """
    Сервис для работы с данными биржевых торгов.
    Содержит бизнес-логику по извлечению и агрегации данных.
    """

    # Публичные методы

    @staticmethod
    async def get_last_trading_dates(
            db: AsyncSession,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить список последних торговых дней с количеством записей.

        Args:
            db: Асинхронная сессия базы данных
            limit: Количество последних дней для возврата (по умолчанию 10)

        Returns:
            Список словарей с ключами 'trading_date' и 'total_records'
        """
        # Гарантируем, что limit положительный
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

    @staticmethod
    async def get_dynamics(
            db: AsyncSession,
            start_date: date,
            end_date: date,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить список торгов за указанный период с фильтрацией.

        Args:
            db: Асинхронная сессия базы данных
            start_date: Начало периода (включительно)
            end_date: Конец периода (включительно)
            oil_id: Фильтр по ID нефтепродукта (опционально)
            delivery_type_id: Фильтр по ID типа поставки (опционально)
            delivery_basis_id: Фильтр по ID базиса поставки (опционально)

        Returns:
            Список словарей с данными торгов
        """

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

    @staticmethod
    async def get_trading_results(
            db: AsyncSession,
            oil_id: Optional[str] = None,
            delivery_type_id: Optional[str] = None,
            delivery_basis_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить список торгов за последнюю доступную дату с фильтрацией.

        Args:
            db: Асинхронная сессия базы данных
            oil_id: Фильтр по ID нефтепродукта (опционально)
            delivery_type_id: Фильтр по ID типа поставки (опционально)
            delivery_basis_id: Фильтр по ID базиса поставки (опционально)

        Returns:
            Список словарей с данными торгов за последнюю дату
        """

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

    @staticmethod
    def _build_dynamics_conditions(
            start_date: date,
            end_date: date,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> List:
        """
        Формирует список условий для запроса динамики торгов.

        Returns:
            Список условий для SQLAlchemy WHERE
        """
        conditions = [
            SpimexTradingResult.date >= start_date,
            SpimexTradingResult.date <= end_date
        ]

        # Добавляем опциональные фильтры
        conditions.extend(
            TradingService._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    @staticmethod
    def _build_results_conditions(
            last_date: date,
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> List:
        """
        Формирует список условий для запроса последних торгов.

        Returns:
            Список условий для SQLAlchemy WHERE
        """
        conditions = [SpimexTradingResult.date == last_date]

        conditions.extend(
            TradingService._build_optional_filters(oil_id, delivery_type_id, delivery_basis_id)
        )

        return conditions

    @staticmethod
    def _build_optional_filters(
            oil_id: Optional[str],
            delivery_type_id: Optional[str],
            delivery_basis_id: Optional[str]
    ) -> List:
        """
        Формирует список опциональных фильтров для запросов.

        Returns:
            Список условий для SQLAlchemy WHERE (только для заданных параметров)
        """
        conditions = []

        if oil_id:
            conditions.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id:
            conditions.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            conditions.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        return conditions

    @staticmethod
    async def _get_last_trading_date(db: AsyncSession) -> Optional[date]:
        """
        Получает последнюю доступную дату торгов.

        Returns:
            Дата последнего торгового дня или None, если данных нет
        """
        result = await db.execute(
            select(func.max(SpimexTradingResult.date))
        )
        return result.scalar()

    @staticmethod
    def _serialize_results(rows: List[SpimexTradingResult]) -> List[Dict[str, Any]]:
        """
        Преобразует список ORM-объектов в список словарей.

        Args:
            rows: Список объектов SpimexTradingResult

        Returns:
            Список словарей с данными
        """
        return [
            TradingResultResponse.model_validate(row).model_dump()
            for row in rows
        ]