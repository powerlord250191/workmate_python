from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import (
    String,
)
from .config_test import (
    DB_NAME,
    DB_PORT,
    DB_HOST,
    DB_USER,
    DB_PASS,
)


class Base(DeclarativeBase):
    pass


TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

str_200 = String(200)


class SpimexTradingResultTest(Base):
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

    def __repr__(self):
        return (f"{self.id}, {self.date}, {self.oil_id}, {self.total}"
                f"{self.volume}, {self.total}, {self.count}, {self.date}")