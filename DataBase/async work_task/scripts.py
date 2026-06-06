from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import SpimexTradingResult
from initial_db import DATABASE_URL, SYNC_DATABASE_URL
from sqlalchemy import create_engine


ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def create_list_object(dict_objects: dict[str]) -> list[SpimexTradingResult]:
    list_objects = []
    for item in dict_objects:
        if item is not None:
            list_objects.append(
                SpimexTradingResult(
                    exchange_product_id=item["exchange_product_id"],
                    exchange_product_name=item["exchange_product_name"],
                    oil_id=item["exchange_product_id"][:4],
                    delivery_basis_id=item["exchange_product_id"][4:7],
                    delivery_basis_name=item["delivery_basis_name"],
                    delivery_type_id=item["exchange_product_id"][-1],
                    volume=item["volume"],
                    total=item["total"],
                    count=item["count"],
                    date=item["date"],
                    created_on=datetime.now(),
                    updated_on=datetime.now(),
                )
            )

    return list_objects


async def insert_data_to_database(data: list[dict[str]]):

    data_objects = create_list_object(data)

    async with AsyncSessionLocal() as session:
        session.add_all(data_objects)
        await session.commit()
