from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from cardsagainst_backend.dao import GameStatsDAO, CardsDAO
from cardsagainst_backend.db import create_tables_if_not_exist, create_engine


def cards_dao_dependency() -> CardsDAO:
    # Will be injected on startup
    raise NotImplementedError


def game_stats_dao_dependency() -> GameStatsDAO:
    # Will be injected on startup
    raise NotImplementedError


def session_dependency() -> async_sessionmaker:
    # Will be injected on startup
    raise NotImplementedError


CardsDAODependency: TypeAlias = Annotated[CardsDAO, Depends(cards_dao_dependency)]
GameStatsDAODependency: TypeAlias = Annotated[
    GameStatsDAO, Depends(game_stats_dao_dependency)
]
SessionDependency: TypeAlias = Annotated[
    async_sessionmaker, Depends(session_dependency)
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_engine()
    logging.getLogger(__name__).warning("Creating tables if not exist...")
    await create_tables_if_not_exist(engine)

    async_session = async_sessionmaker(engine)
    cards_dao = CardsDAO(async_session)
    game_stats_dao = GameStatsDAO(async_session)

    app.dependency_overrides = {
        session_dependency: lambda: async_session,
        cards_dao_dependency: lambda: cards_dao,
        game_stats_dao_dependency: lambda: game_stats_dao,
    }

    yield
