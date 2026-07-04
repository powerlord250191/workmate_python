from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    String,
)


str_200 = String(200)


class Base(DeclarativeBase):
    pass


class SpimexTradingResult(Base):
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(String(400))
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)
    oil_id: Mapped[str] = mapped_column(str_200)
    delivery_basis_id: Mapped[str] = mapped_column(str_200)
    delivery_basis_name: Mapped[str] = mapped_column(str_200)
    delivery_type_id: Mapped[str] = mapped_column(str_200)
    volume: Mapped[float]
    total: Mapped[float]
    count: Mapped[int]
    date: Mapped[datetime]

    # def __repr__(self):
    #     return (f"{self.id}, {self.date}, {self.oil_id}, {self.total}"
    #             f"{self.volume}, {self.total}, {self.count}, {self.date}")
