from uuid import uuid4

from sqlalchemy import select

from db import async_session
from models import Punchline, Setup
from lobby import Deck, PunchlineCard, SetupCard


class CardsDAO:
    def __init__(self, async_session=async_session) -> None:
        self.async_session = async_session

    async def get_setups(self, deck_id: str) -> Deck[SetupCard]:
        async with self.async_session() as session:
            result = await session.execute(select(Setup))

            return Deck(
                cards=[
                    SetupCard(
                        id=row.id,
                        text=row.text,
                        case=row.variant,
                        starts_with_punchline=row.starts_with_punchline,
                    )
                    for row in result.all()
                ]
            )

    async def get_punchlines(self, deck_id: str) -> Deck[PunchlineCard]:
        async with self.async_session() as session:
            result = await session.execute(select(Punchline))

            return Deck(
                cards=[
                    PunchlineCard(
                        id=row.id,
                        text=row.text,
                    )
                    for row in result.all()
                ]
            )


cards_dao = CardsDAO()
