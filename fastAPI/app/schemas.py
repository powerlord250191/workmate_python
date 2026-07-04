from typing import Optional
import os
from pydantic import BaseModel, Field, field_validator
from datetime import date as date_type, datetime
from config import (
    DB_PASS,
    DB_USER,
    DB_PORT,
    DB_HOST,
    DB_NAME
)


class Config:
    DATABASE_URL = (f"postgresql+asyncpg://"
                    f"{DB_USER}:{DB_PASS}@"
                    f"{DB_HOST}:{DB_PORT}/"
                    f"{DB_NAME}")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_RESET_TIME = "14:11"


class TradingResultBase(BaseModel):
    exchange_product_id: str = Field(..., min_length=1, max_length=50)
    exchange_product_name: str = Field(..., min_length=1, max_length=200)
    oil_id: str = Field(..., min_length=1, max_length=10)
    delivery_basis_id: str = Field(..., min_length=1, max_length=10)
    delivery_basis_name: str = Field(..., min_length=1, max_length=200)
    delivery_type_id: str = Field(..., min_length=1, max_length=1)
    volume: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    count: float = Field(..., ge=0)
    date: date_type = Field(...)


class TradingResultResponse(TradingResultBase):
    id: int
    created_on: datetime = None
    updated_on: datetime = None

    class Config:
        from_attributes = True


class TradingDateResponse(BaseModel):
    trading_date: date_type
    total_records: int = Field(..., ge=0)


class LastTradingDatesParams(BaseModel):
    limit: int = Field(..., ge=1, le=365, description="Количество последних торговых дней (1-365)")


class DynamicsParams(BaseModel):
    start_date: date_type = Field(..., description="Дата начала периода (обязательно)")
    end_date: date_type = Field(..., description="Дата конца периода (обязательно)")
    oil_id: Optional[str] = Field(None, min_length=1, max_length=10, description="ID нефтепродукта")
    delivery_type_id: Optional[str] = Field(None, min_length=1, max_length=1, description="ID типа поставки")
    delivery_basis_id: Optional[str] = Field(None, min_length=1, max_length=10, description="ID базиса поставки")

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_dates(cls, v):
        if v > date_type.today():
            raise ValueError('Дата не может быть в будущем')
        return v

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        start_date = info.data.get('start_date')
        if start_date and v < start_date:
            raise ValueError('Дата начала должна быть раньше даты конца')
        return v


class TradingResultsParams(BaseModel):
    oil_id: Optional[str] = Field(None, min_length=1, max_length=10, description="ID продукта")
    delivery_type_id: Optional[str] = Field(None, min_length=1, max_length=1, description="ID типа поставки")
    delivery_basis_id: Optional[str] = Field(None, min_length=1, max_length=10, description="ID базиса поставки")
