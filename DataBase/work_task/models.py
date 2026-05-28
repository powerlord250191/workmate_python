from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime
)


class Base(DeclarativeBase):
    pass


class SpimexTradingResult(Base):
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(String, nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(String(400))
    oil_id: Mapped[str] = mapped_column(String(200))
    delivery_basis_id: Mapped[str] = mapped_column(String(200))
    delivery_basis_name: Mapped[str] = mapped_column(String(200))
    delivery_type_id: Mapped[str] = mapped_column(String(200))
    volume: Mapped[float] = mapped_column(Float)
    total: Mapped[float] = mapped_column(Float)
    count: Mapped[int] = mapped_column(Integer)
    date: Mapped[DateTime] = mapped_column(DateTime)
    created_on: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    updated_on: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
