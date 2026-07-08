import pytest
from datetime import datetime, date

from .database_test import SpimexTradingResultTest


class TestTradingRepository:

    @pytest.mark.asyncio
    async def test_get_last_trading_dates(self, repository, session, sample_trading_data):
        for item in sample_trading_data:
            session.add(SpimexTradingResultTest(**item))
        await session.commit()

        result = await repository.get_last_trading_dates(limit=1)
        assert len(result) == 1
        assert result[0]["trading_date"] == datetime(2024, 1, 16)

        result = await repository.get_last_trading_dates(limit=2)
        assert len(result) == 2
        assert result[0]["trading_date"] == datetime(2024, 1, 16)
        assert result[1]["trading_date"] == datetime(2024, 1, 15)

    @pytest.mark.asyncio
    async def test_get_dynamics_with_filters(self, repository, session, sample_trading_data):
        for item in sample_trading_data:
            session.add(SpimexTradingResultTest(**item))
        await session.commit()

        result_correct = await repository.get_dynamics(
            start_date=datetime(2024, 1, 15, 00, 00, 00),
            end_date=datetime(2024, 1, 16, 00, 00, 00),
            oil_id="A100",
        )

        result_no_correct_data = await repository.get_dynamics(
            start_date=datetime(2020, 1, 15, 00, 00, 00),
            end_date=datetime(2020, 1, 16, 00, 00, 00),
            oil_id="A100",
        )

        result_no_correct_oil_id = await repository.get_dynamics(
            start_date=datetime(2020, 1, 15, 00, 00, 00),
            end_date=datetime(2020, 1, 16, 00, 00, 00),
            oil_id="cdsdfd",
        )

        assert len(result_correct) == 2
        assert all(r["oil_id"] == "A100" for r in result_correct)
        assert result_no_correct_data == []
        assert result_no_correct_oil_id == []

    @pytest.mark.asyncio
    async def test_get_trading_results(self, repository, session, sample_trading_data):
        for item in sample_trading_data:
            session.add(SpimexTradingResultTest(**item))
        await session.commit()

        result = await repository.get_trading_results()

        assert len(result) == 1
        assert result[0]["date"] == date(2024, 1, 16)
        assert result[0]["oil_id"] == "A100"
        assert result[0]["delivery_basis_name"] == "ст. Новоярославская"
        assert result[0]["volume"] == 120.0
        assert result[0]["total"] == 11317440.0
        assert result[0]["count"] == 2

    @pytest.mark.parametrize("oil_id,expected_count", [
        ("A100", 2),
        ("A692", 1),
        (None, 3),
    ])
    @pytest.mark.asyncio
    async def test_get_dynamics_parametrize(
        self,
        repository,
        session,
        sample_trading_data,
        oil_id,
        expected_count,
    ):
        for item in sample_trading_data:
            session.add(SpimexTradingResultTest(**item))
        await session.commit()

        result = await repository.get_dynamics(
            start_date=datetime(2024, 1, 15, 00, 00, 00),
            end_date=datetime(2024, 1, 16, 00, 00, 00),
            oil_id=oil_id,
        )

        assert len(result) == expected_count