from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TypeVar, Generic


@dataclass
class SetupCard:
    id: int
    text: str
    case: str
    starts_with_punchline: bool


@dataclass
class PunchlineCard:
    id: int
    text: list[tuple[str, list[str]]]


AnyCard = TypeVar("AnyCard", bound=SetupCard | PunchlineCard)


class Deck(Generic[AnyCard]):
    def __init__(self, cards: list[AnyCard]) -> None:
        self.cards = cards
        self._dump: list[AnyCard] = []
        self._shuffle()
        self.mapping = {card.id: card for card in cards}

    def get_card_by_uuid(self, card_id):
        return self.mapping[card_id]

    def _shuffle(self):
        random.shuffle(self.cards)

    def get_card(self) -> AnyCard:
        if not self.cards:
            self.cards, self._dump = self._dump, []
            self._shuffle()

        return self.cards.pop()

    def dump(self, cards: list[AnyCard]) -> None:
        self._dump.extend(cards)
