from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy import insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from dao import cards_dao
from db import async_session, engine
from lobby import PunchlineCard, SetupCard
from models import Punchline, Setup, metadata
from config import config


@pytest.fixture(scope="session", autouse=True)
async def set_test_environment() -> None:
    config.configure(FORCE_ENV_FOR_DYNACONF="test")


@pytest.fixture(autouse=True)
async def cleanup_database(set_test_environment: None) -> None:
    tables = ("punchlines", "setups")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        for table in tables:
            await conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@pytest.fixture
async def punchline_card(session: AsyncSession) -> None:
    await session.execute(insert(Punchline).values(text=[("value", ["variant"])]))
    await session.commit()


@pytest.fixture
async def setup_card(session: AsyncSession) -> None:
    await session.execute(
        insert(Setup).values(variant="variant", starts_with_punchline=True, text="text")
    )
    await session.commit()


@pytest.mark.usefixtures("punchline_card")
async def test_insert_punchline_card(session: AsyncSession) -> None:
    ((punchline_card,),) = await session.execute(select(Punchline))
    assert isinstance(punchline_card, Punchline)


@pytest.mark.usefixtures("setup_card")
async def test_insert_setup_card(session: AsyncSession) -> None:
    ((setup_card,),) = await session.execute(select(Setup))
    assert isinstance(setup_card, Setup)


@pytest.mark.usefixtures("setup_card")
async def test_get_setups() -> None:
    deck = await cards_dao.get_setups("123")
    assert isinstance(deck.get_card(), SetupCard)


@pytest.mark.usefixtures("punchline_card")
async def test_get_punchlines() -> None:
    deck = await cards_dao.get_punchlines("123")
    assert isinstance(deck.get_card(), PunchlineCard)
