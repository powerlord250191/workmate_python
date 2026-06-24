from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime


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
    date: date


class TradingResultResponse(TradingResultBase):
    id: int
    created_on: datetime
    updated_on: datetime

    class Config:
        from_attributes = True


class TradingDateResponse(BaseModel):
    trading_date: date
    total_records: int = Field(..., ge=0)
