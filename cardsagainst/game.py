from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from cardsagainst.deck import Deck, PunchlineCard, SetupCard
from cardsagainst.settings import LobbySettings


class Game:
    def __init__(
        self,
        punchlines: Deck[PunchlineCard],
        setups: Deck[SetupCard],
        settings: LobbySettings,
    ):
        self.id = uuid4().hex
        self.punchlines = punchlines
        self.setups = setups
        self.settings = settings


@dataclass
class GameStarted:
    game: Game
