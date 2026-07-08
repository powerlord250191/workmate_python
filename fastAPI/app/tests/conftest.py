import asyncio
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.repositories import TradingRepository
from app.routers import get_trading_repository
from .database_test import Base, SpimexTradingResultTest, TEST_DATABASE_URL


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine():

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session_factory(engine):

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture(scope="function")
async def session(session_factory):
    async with session_factory() as session:
        yield session


@pytest.fixture
def repository(session_factory):
    return TradingRepository(session_factory)


@pytest.fixture(scope="function")
async def override_repository(session_factory):
    def _get_repo_override():
        return TradingRepository(session_factory)
    app.dependency_overrides[get_trading_repository] = _get_repo_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(override_repository):
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_trading_data():
    return [
        {
            "exchange_product_id": "A100ANK060F",
            "exchange_product_name": "Бензин (АИ-100-К5)",
            "oil_id": "A100",
            "delivery_basis_id": "ANK",
            "delivery_basis_name": "Ангарск-группа станций",
            "delivery_type_id": "F",
            "volume": 60.0,
            "total": 5607900.0,
            "count": 1,
            "date": datetime(2024, 1, 15, 0, 0, 0),
        },
        {
            "exchange_product_id": "A692ALL060J",
            "exchange_product_name": "Бензин (АИ-92-К5)",
            "oil_id": "A692",
            "delivery_basis_id": "ALL",
            "delivery_basis_name": "ГОСТ",
            "delivery_type_id": "J",
            "volume": 35.0,
            "total": 153126120.0,
            "count": 2580,
            "date": datetime(2024, 1, 15, 0, 0, 0),
        },
        {
            "exchange_product_id": "A100NVY060F",
            "exchange_product_name": "Бензин (АИ-100-К5)",
            "oil_id": "A100",
            "delivery_basis_id": "NVY",
            "delivery_basis_name": "ст. Новоярославская",
            "delivery_type_id": "F",
            "volume": 120.0,
            "total": 11317440.0,
            "count": 2,
            "date": datetime(2024, 1, 16, 0, 0, 0),
        },
    ]


@pytest.fixture
async def populated_db(session, sample_trading_data):
    for item in sample_trading_data:
        record = SpimexTradingResultTest(**item)
        session.add(record)
    await session.commit()
    return session


@pytest.fixture
def mock_cache(monkeypatch):
    class MockCache:
        async def get(self, prefix, params):
            return None

        async def set(self, prefix, params, data):
            pass

        async def get_or_set(self, prefix, params, func):
            return await func()

    monkeypatch.setattr("fastAPI.app.repositories.cache_service", MockCache())
    return MockCache()


@pytest.fixture
def repository_with_mock_cache(mock_cache, session_factory):
    return TradingRepository(session_factory)