import os
from typing import AsyncGenerator

import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Punchline, Setup


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(os.environ["PG_DATABASE"])
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def punchline_card(session: AsyncSession) -> None:
    await session.execute(
        insert(Punchline).values(text=[("value", ["variant"])]).returning(Punchline.id)
    )


@pytest.fixture
async def setup_card(session: AsyncSession) -> None:
    await session.execute(
        insert(Setup)
        .values(variant="variant", starts_with_punchline=True, text="text")
        .returning(Punchline.id)
    )


@pytest.mark.usefixtures("punchline_card")
async def test_insert_punchline_card(session: AsyncSession) -> None:
    ((punchline_card,),) = await session.execute(select(Punchline))
    assert isinstance(punchline_card, Punchline)


@pytest.mark.usefixtures("setup_card")
async def test_insert_punchline_card(session: AsyncSession) -> None:
    ((setup_card,),) = await session.execute(select(Setup))
    assert isinstance(setup_card, Setup)
