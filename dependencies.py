from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from dao import CardsDAO
from db import create_engine, create_tables_if_not_exist


def cards_dao_dependency() -> CardsDAO:
    # Will be injected on startup
    raise NotImplementedError


CardsDAODependency: TypeAlias = Annotated[CardsDAO, Depends(cards_dao_dependency)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_engine()
    await create_tables_if_not_exist(engine)

    async_session = async_sessionmaker(engine)
    cards_dao = CardsDAO(async_session)

    app.dependency_overrides = {
        cards_dao_dependency: lambda: cards_dao,
    }

    yield
