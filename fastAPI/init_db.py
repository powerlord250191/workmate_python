import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.schemas import Config


async def init():
    engine = create_async_engine(Config.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init())