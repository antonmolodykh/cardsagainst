from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config import config
from models import metadata


def create_engine() -> AsyncEngine:
    return create_async_engine(config.db.url)


async def create_tables_if_not_exist(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
