from __future__ import annotations

import random
from typing import Collection, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field
from typing_extensions import Annotated

lobbies = {}


class CardNotInPlayerHandError(Exception):
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
    def owner_changed(self, player: Player):
        pass

    def player_disconnected(self, player: Player):
        pass

    def player_joined(self, player: Player):
        pass

    def player_left(self, player: Player):
        pass

    def player_connected(self, player: Player):
        pass

    def game_started(self, player: Player):
        pass

    def turn_started(self, turn_duration: int, lead: Player):
        pass

    def player_ready(self, player: Player):
        pass

    def table_card_opened(self, card_on_table: CardOnTable):
        pass

    def turn_ended(self, winner: Player, card: PunchlineCard):
        pass

    def all_players_ready(self):
        pass


class Card(BaseModel):
    uuid: Annotated[uuid4, Field(default_factory=uuid4)]


class SetupCard(Card):
    text: str
    case: str
    starts_with_punchline: bool


class PunchlineCard(Card):
    text: dict[str, str]


class Profile(BaseModel):
    name: str
    emoji: str
    background_color: str


class Player:
    observer: LobbyObserver
    uuid: str
    hand: list[PunchlineCard]
    score: int = 0
    profile: Profile
    is_ready = False
    is_connected: bool = False

    def __init__(self, profile: Profile) -> None:
        self.profile = profile
        self.hand = []
        self.uuid = uuid4().hex
        self.observer = LobbyObserver()

    def set_connected(self) -> None:
        self.is_connected = True

    def set_disconnected(self) -> None:
        self.observer = LobbyObserver()
        self.is_connected = False

    def add_punchline_card(self, card: PunchlineCard):
        self.hand.append(card)


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
        self._shuffle()
        self.mapping = {card.uuid: card for card in cards}

    def get_card_by_uuid(self, card_uuid):
        return self.mapping[card_uuid]

    def _shuffle(self):
        random.shuffle(self.cards)

    def get_card(self) -> AnyCard:
        if not self.cards:
            self.cards, self.dump = self.dump, []
            self._shuffle()

        return self.cards.pop()

    def dump(self, card: AnyCard) -> None:
        self.dump.append(card)


class LobbySettings(BaseModel):
    turn_duration: int | None = 20


class Judgement:
    def __init__(self, lobby: Lobby):
        self.lobby = lobby

    def open_punchline_card(self, player: Player, card_on_table: CardOnTable) -> None:
        if self.lobby.lead is not player:
            raise PlayerNotDealerError

        card_on_table.is_open = True
        for pl in self.lobby.all_players:
            pl.observer.table_card_opened(card_on_table)

    def pick_turn_winner(self, card) -> None:
        card_on_table = self.lobby.get_card_from_table(card=card)
        card_on_table.player.score += 1

        for pl in self.lobby.all_players:
            pl.observer.turn_ended(card_on_table.player, card)


class Lobby:
    uid: uuid4
    players: list[Player]
    lead: Player
    owner: Player | None
    setup_card: SetupCard
    table: list[CardOnTable]
    punchlines: Deck[PunchlineCard]
    setups: Deck[SetupCard]
    observer: LobbyObserver
    settings: LobbySettings

    HAND_SIZE = 5

    def __init__(
        self,
        players: Collection[Player],
        lead: Player,
        owner: Player,
        setups: Deck[SetupCard],
        punchlines: Deck[PunchlineCard],
    ) -> None:
        self.players = list(players)
        self.lead = lead
        self.owner = owner
        self.setup_card = setups.get_card()
        self.table = []
        self.uid = uuid4()
        self.punchlines = punchlines
        self.setups = setups
        self.settings = LobbySettings()
        self.state = None

    @property
    def all_players(self):
        return [self.lead, *self.players]

    def all_players_except(self, player: Player):
        return [p for p in self.all_players if p is not player]

    def change_owner(self) -> None:
        self.owner = None
        for player in self.players:
            if player.is_connected:
                self.owner = player

    def change_lead(self) -> None:
        self.players.append(self.lead)
        self.lead = self.players.pop(0)

    def change_setup_card(self, card: SetupCard) -> None:
        self.setup_card = card

    def choose_punchline_card(self, player: Player, card: PunchlineCard) -> None:
        if card not in player.hand:
            raise CardNotInPlayerHandError

        self.table.append(CardOnTable(card=card, player=player))
        player.hand.remove(card)

        for pl in self.all_players:
            pl.observer.player_ready(player)

        if len(self.table) == len(self.players):
            self.state = Judgement(self)
            for pl in self.all_players:
                pl.observer.all_players_ready()

    def get_card_from_table(self, card) -> CardOnTable:
        for card_on_table in self.table:
            if card is card_on_table.card:
                return card_on_table
        raise NotImplemented

    def set_connected(self, player: Player):
        player.set_connected()
        if not self.owner:
            self.owner = player
        for pl in self.all_players_except(player):
            pl.observer.player_connected(player)

    def set_disconnected(self, player: Player):
        was_owner = False

        player.set_disconnected()
        if player is self.owner:
            was_owner = True
            self.change_owner()

        for pl in self.all_players_except(player):
            pl.observer.player_disconnected(player)
            if was_owner:
                pl.observer.owner_changed(player)
        # обработать если осталось менее 2 игроков

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
            for _ in range(self.HAND_SIZE):
                pl.add_punchline_card(self.punchlines.get_card())
            pl.observer.game_started(pl)

        self.start_turn()

    def start_turn(self):
        for pl in self.players:
            pl.observer.turn_started(
                turn_duration=self.settings.turn_duration, lead=self.lead
            )
