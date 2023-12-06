from uuid import uuid4

from models import Punchline
from lobby import Deck, PunchlineCard, SetupCard


class CardsDAO:
    def get_setups(self, deck_id: str) -> Deck[SetupCard]:
        return setups_deck

    def get_punchlines(self, deck_id: str) -> Deck[PunchlineCard]:
        return punchlines_deck


cards_dao = CardsDAO()
