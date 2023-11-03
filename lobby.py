from __future__ import annotations

import random
from typing import Collection, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field
from typing_extensions import Annotated

lobbies = {}


class PlayerNotPunchlineCardHolderError(Exception):
    pass


class PlayerNotDealerError(Exception):
    pass


class PlayerNotOwnerError(Exception):
    pass


# class State(Enum):
#     MOVE = "move"
#     JUDGING = "judging"
#     PENDING_START = "pending start"
#     FINISHED = "finished"


class LobbyObserver:
    def player_disconnected(self, player: Player):
        pass

    def player_joined(self, player: Player):
        pass

    def player_left(self, player: Player):
        pass

    def player_connected(self, player: Player):
        pass

    def game_started(self):
        pass

    def turn_started(self, turn_duration: int):
        pass


class Card(BaseModel):
    uid: Annotated[uuid4, Field(default_factory=uuid4)]


class SetupCard(Card):
    pass


class PunchlineCard(Card):
    pass


class Profile(BaseModel):
    name: str
    emoji: str
    background_color: str


class Player:
    observer: LobbyObserver
    uid: str
    punchline_cards: list[PunchlineCard]
    score: int = 0
    profile: Profile
    is_connected: bool = False

    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.punchline_cards = []
        self.uid = uuid4().hex
        self.observer = LobbyObserver()

    def set_connected(self) -> None:
        self.is_connected = True

    def set_disconnected(self) -> None:
        self.observer = LobbyObserver()
        self.is_connected = False


class CardOnTable:
    card: PunchlineCard
    player: Player
    is_open: bool = False

    def __init__(self, card: PunchlineCard, player: Player) -> None:
        self.card = card
        self.player = player


AnyCard = TypeVar("AnyCard", bound=Card)


class Deck(Generic[AnyCard]):
    def __init__(self, cards: list[AnyCard]) -> None:
        self.cards = cards
        self.dump = []

    def get_random_card(self) -> AnyCard:
        if not self.cards:
            random.shuffle(self.dump)
            self.cards, self.dump = self.dump, []

        card = self.cards.pop(random.randint(0, len(self.cards) - 1))
        self.dump.append(card)
        return card


class LobbySettings(BaseModel):
    turn_duration: int | None = 20


class Lobby:
    uid: uuid4
    players: list[Player]
    lead: Player
    owner: Player
    setup_card: SetupCard
    table: list[CardOnTable]
    punchlines: Deck[PunchlineCard]
    setups: Deck[SetupCard]
    observer: LobbyObserver
    settings: LobbySettings

    def __init__(
        self,
        players: Collection[Player],
        lead: Player,
        owner: Player,
        setups: Deck[SetupCard],
        punchlines: Deck[PunchlineCard],
        observer: LobbyObserver,
    ) -> None:
        self.players = list(players)
        self.lead = lead
        self.owner = owner
        self.setup_card = setups.get_random_card()
        self.table = []
        self.uid = uuid4()
        self.punchlines = punchlines
        self.setups = setups
        self.observer = observer
        self.settings = LobbySettings()

    @property
    def all_players(self):
        return [self.lead, *self.players]

    def _all_players_except(self, player: Player):
        return [p for p in self.all_players if p is not player]

    def change_lead(self) -> None:
        self.players.append(self.lead)
        self.lead = self.players.pop(0)

    def change_setup_card(self, card: SetupCard) -> None:
        self.setup_card = card

    def choose_punchline_card(self, player: Player, card: PunchlineCard) -> None:
        if card not in player.punchline_cards:
            raise PlayerNotPunchlineCardHolderError
        self.table.append(CardOnTable(card=card, player=player))
        player.punchline_cards.remove(card)

    def get_card_from_table(self, card) -> CardOnTable:
        for card_on_table in self.table:
            if card is card_on_table.card:
                return card_on_table
        raise NotImplemented

    def open_punchline_card(self, player: Player, card: PunchlineCard) -> None:
        if self.lead is not player:
            raise PlayerNotDealerError

        card_on_table = self.get_card_from_table(card=card)
        card_on_table.is_open = True

    def lead_choose_punchline_card(self, card: PunchlineCard) -> None:
        card_on_table = self.get_card_from_table(card=card)
        card_on_table.player.score += 1

    def set_connected(self, player: Player):
        player.set_connected()
        for pl in self._all_players_except(player):
            pl.observer.player_connected(player)

    def set_disconnected(self, player: Player):
        player.set_disconnected()
        for pl in self._all_players_except(player):
            pl.observer.player_disconnected(player)

    def add_player(self, player: Player):
        for pl in self.all_players:
            pl.observer.player_joined(player)
        self.players.append(player)

    # def remove_player(self, player: Player):
    #     for pl in self._all_players_except(player):
    #         pl.observer.player_left(player)
    #     self.players.remove(player)

    def start_game(self, player: Player, lobby_settings: LobbySettings) -> None:
        if player is not self.owner:
            raise PlayerNotOwnerError

        self.settings = lobby_settings
        for pl in self.all_players:
            pl.observer.game_started()
            pl.observer.turn_started(turn_duration=self.settings.turn_duration)

