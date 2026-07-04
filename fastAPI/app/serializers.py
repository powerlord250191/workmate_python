from models import SpimexTradingResult
from schemas import TradingResultResponse


class TradingSerializer:

    @staticmethod
    def serialize_trading_results(rows: list[SpimexTradingResult]) -> list[TradingResultResponse]:
        return [
            TradingResultResponse.model_validate(row).model_dump()
            for row in rows if row
        ]

    @staticmethod
    def serialize_trading_dates(rows: list[dict]) -> list[dict]:
        return rows