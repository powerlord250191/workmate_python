from models import SpimexTradingResult
from schemas import TradingResultResponse


def serialize_trading_results(rows: list[SpimexTradingResult]) -> list[TradingResultResponse]:
    return [
        TradingResultResponse.model_validate(row).model_dump()
        for row in rows if row
    ]


def serialize_trading_dates(rows: list[dict]) -> list[dict]:
    return rows