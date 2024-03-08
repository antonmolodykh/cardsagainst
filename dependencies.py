from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from dao import CardsDAO
from db import create_engine, create_tables_if_not_exist


def cards_dao_dependency() -> CardsDAO:
    # Will be injected on startup
    raise NotImplementedError


def session_dependency() -> async_sessionmaker:
    # Will be injected on startup
    raise NotImplementedError


CardsDAODependency: TypeAlias = Annotated[CardsDAO, Depends(cards_dao_dependency)]
SessionDependency: TypeAlias = Annotated[async_sessionmaker, Depends(session_dependency)]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_engine()
    logging.getLogger(__name__).warning("Creating tables if not exist...")
    await create_tables_if_not_exist(engine)

    async_session = async_sessionmaker(engine)
    cards_dao = CardsDAO(async_session)

    app.dependency_overrides = {
        session_dependency: lambda: async_session,
        cards_dao_dependency: lambda: cards_dao,
    }

    yield
