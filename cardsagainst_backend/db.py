from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from cardsagainst_backend.config import config
from cardsagainst_backend.models import metadata


def create_engine() -> AsyncEngine:
    return create_async_engine(config.db.url)


async def create_tables_if_not_exist(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
