from __future__ import annotations

import asyncio
import traceback
from asyncio import Task
from enum import StrEnum
from typing import Generic, MutableMapping, TypeVar
from uuid import uuid4
from weakref import WeakValueDictionary

from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import select
from starlette.websockets import WebSocketDisconnect
from typing_extensions import Annotated

from config import config
from dao import CardsDAO
from dependencies import CardsDAODependency, lifespan, SessionDependency
from lobby import (
    CardOnTable,
    GameAlreadyStartedError,
    Gathering,
    Judgement,
    Lobby,
    LobbyObserver,
    LobbySettings,
    Player,
    Profile,
    PunchlineCard,
    SetupCard,
    Turns,
    UnknownPlayerError,
)
from models import Changelog

observers: list[LobbyObserver] = []

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

player_by_token: MutableMapping[str, Player] = WeakValueDictionary()
lobbies: dict[str, Lobby] = {}
remove_player_tasks: dict[str, Task] = {}


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


def get_player_data_from_player(player: Player) -> PlayerData:
    return PlayerData(
        uuid=player.uuid,
        name=player.profile.name,
        emoji=player.profile.emoji,
        state=PlayerState.PENDING,
        score=player.score,
        is_connected=player.is_connected,
    )


class ChangelogData(ApiModel):
    version: str
    text: str


class ChangelogResponse(ApiModel):
    changelog: list[ChangelogData]
    current_version: str


class PlayerIdData(ApiModel):
    uuid: str


class SetupData(ApiModel):
    id: int
    text: str
    case: str
    starts_with_punchline: bool

    @classmethod
    def from_setup(cls, setup: SetupCard):
        return cls(
            id=setup.id,
            text=setup.text,
            case=setup.case,
            starts_with_punchline=setup.starts_with_punchline,
        )


class PunchlineData(ApiModel):
    id: int
    text: list[tuple[str, list[str]]]

    @classmethod
    def from_card(cls, card: PunchlineCard):
        return cls(id=card.id, text=card.text)


class CardOnTableData(ApiModel):
    card: PunchlineData | None
    is_picked: bool
    author: str | None


class TableCardOpenedData(ApiModel):
    index: int
    card: PunchlineData


class TurnEndedData(ApiModel):
    winner_uuid: str
    card_id: int
    score: int


class GameFinishedData(ApiModel):
    winner_uuid: str


class GameStartedData(ApiModel):
    hand: list[PunchlineData]


class RemotePlayer(LobbyObserver):
    def __init__(self, websocket: WebSocket, lobby: Lobby, player: Player) -> None:
        self.lobby = lobby
        self.websocket = websocket
        self.player = player
        self._queue = asyncio.Queue()

    def owner_changed(self, player: Player):
        self._queue.put_nowait(
            Event(id=1, type="ownerChanged", data=PlayerIdData(uuid=player.uuid))
        )

    def player_joined(self, player: Player):
        self._queue.put_nowait(
            Event(id=1, type="playerJoined", data=get_player_data_from_player(player))
        )

    def player_left(self, player: Player):
        self._queue.put_nowait(
            Event(id=1, type="playerLeft", data=PlayerIdData(uuid=player.uuid))
        )

    def player_connected(self, player: Player):
        self._queue.put_nowait(
            Event(id=2, type="playerConnected", data=PlayerIdData(uuid=player.uuid))
        )

    def player_disconnected(self, player: Player):
        self._queue.put_nowait(
            Event(id=1, type="playerDisconnected", data=PlayerIdData(uuid=player.uuid))
        )

    def game_started(self, player: Player):
        self._queue.put_nowait(
            Event(
                id=1,
                type="gameStarted",
                data=GameStartedData(
                    hand=[PunchlineData.from_card(item) for item in player.hand]
                ),
            )
        )

    def turn_started(
        self,
        setup: SetupCard,
        turn_duration: int | None,
        lead: Player,
        turn_count: int,
        card: PunchlineCard | None = None,
    ):
        self._queue.put_nowait(
            Event(
                id=1,
                type="turnStarted",
                data=TurnStartedData(
                    setup=SetupData.from_setup(setup),
                    turn_duration=turn_duration,
                    lead_uuid=lead.uuid,
                    turn_count=turn_count,
                    card=PunchlineData.from_card(card) if card else None,
                ),
            )
        )

    def player_ready(self, player: Player):
        self._queue.put_nowait(
            Event(id=1, type="playerReady", data=PlayerIdData(uuid=player.uuid))
        )

    def table_card_opened(self, card_on_table: CardOnTable):
        self._queue.put_nowait(
            Event(
                id=1,
                type="tableCardOpened",
                data=TableCardOpenedData(
                    index=self.lobby.table.index(card_on_table),
                    card=PunchlineData.from_card(card_on_table.card),
                ),
            )
        )

    def turn_ended(self, winner: Player, card: PunchlineCard):
        self._queue.put_nowait(
            Event(
                id=1,
                type="turnEnded",
                data=TurnEndedData(
                    winner_uuid=winner.uuid, card_id=card.id, score=winner.score
                ),
            )
        )

    def all_players_ready(self):
        self._queue.put_nowait(Event(id=1, type="allPlayersReady", data=None))

    def game_finished(self, winner: Player):
        self._queue.put_nowait(
            Event(
                id=1,
                type="gameFinished",
                data=GameFinishedData(winner_uuid=winner.uuid),
            )
        )

    def welcome(self):
        selected_card = self.lobby.get_selected_card(self.player)
        self._queue.put_nowait(
            Event(
                id=1,
                type="welcome",
                data=LobbyState(
                    state=GameState(type(self.lobby.state).__name__.lower()),
                    turn_count=self.lobby.turn_count,
                    players=[
                        get_player_data_from_player(player)
                        for player in self.lobby.all_players
                    ],
                    table=[
                        CardOnTableData(
                            card=PunchlineData.from_card(card_on_table.card)
                            if card_on_table.is_open
                            else None,
                            is_picked=is_card_picked(self.lobby, card_on_table),
                            author=(
                                card_on_table.player.profile.name
                                if is_card_picked(self.lobby, card_on_table)
                                else None
                            ),
                        )
                        for card_on_table in self.lobby.table
                    ],
                    hand=[PunchlineData.from_card(item) for item in self.player.hand],
                    setup=(
                        SetupData.from_setup(self.lobby.state.setup)
                        if isinstance(self.lobby.state, Judgement | Turns)
                        else None
                    ),
                    timeout=self.lobby.settings.turn_duration,
                    lead_uuid=self.lobby.lead.uuid if self.lobby.lead else None,
                    owner_uuid=self.lobby.owner.uuid,
                    self_uuid=self.player.uuid,
                    selected_card=(
                        PunchlineData.from_card(selected_card)
                        if selected_card
                        else None
                    ),
                ),
            )
        )

    async def send_events(self):
        while True:
            event = await self._queue.get()
            data = event.model_dump(by_alias=True)
            print(f"Event: {data}")
            await self.websocket.send_json(data)

    async def handle_event(self, json_data: dict, cards_dao: CardsDAO) -> None:
        match json_data["type"]:
            case "startGame":
                event = Event[StartGameData].model_validate(json_data)
                self.player.start_game(
                    settings=LobbySettings(
                        turn_duration=event.data.turn_duration,
                        winning_score=event.data.winning_score or config.winning_score,
                    ),
                    setups=await cards_dao.get_setups(deck_id="one"),
                    punchlines=await cards_dao.get_punchlines(deck_id="one"),
                )
            case "makeTurn":
                event = Event[MakeTurnData].model_validate(json_data)
                try:
                    card = self.lobby.punchlines.get_card_by_uuid(int(event.data.id))
                except KeyError:
                    print("unknown card")
                    return
                self.player.make_turn(card)
            case "openTableCard":
                event = Event[OpenTableCardData].model_validate(json_data)
                self.player.open_table_card(self.lobby.table[event.data.index])
            case "pickTurnWinner":
                event = Event[PickTurnWinnerData].model_validate(json_data)
                try:
                    card = self.lobby.punchlines.get_card_by_uuid(int(event.data.id))
                except KeyError:
                    return
                self.player.pick_turn_winner(card)
            case "continueGame":
                self.player.continue_game()


class ConnectRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    name: str
    emoji: str


class PlayerState(StrEnum):
    DEFAULT = "default"
    READY = "ready"
    LEADING = "leading"
    PENDING = "pending"


class CardTextCase(StrEnum):
    NOM = "nom"
    GEN = "gen"
    DAT = "dat"
    ACC = "acc"
    INST = "inst"
    PREP = "prep"


class GameState(StrEnum):
    GATHERING = "gathering"
    TURNS = "turns"
    JUDGEMENT = "judgement"
    CONGRATS = "congrats"
    FINISHED = "finished"


class TableCard(ApiModel):
    id: int
    text: dict[CardTextCase, str]
    is_opened: bool


class PlayerData(ApiModel):
    uuid: str
    name: str
    emoji: str
    state: PlayerState
    score: int
    is_connected: bool


AnyEventData = TypeVar("AnyEventData", bound=ApiModel)


class Event(ApiModel, Generic[AnyEventData]):
    id: int
    type: str
    data: AnyEventData | None


class StartGameData(ApiModel):
    turn_duration: int | None = None
    winning_score: int | None = None


class MakeTurnData(ApiModel):
    id: int


class OpenTableCardData(ApiModel):
    index: int


class PickTurnWinnerData(ApiModel):
    id: int


class TurnStartedData(ApiModel):
    setup: SetupData
    turn_duration: int | None
    lead_uuid: str
    turn_count: int
    card: PunchlineData | None = None


class LobbyState(ApiModel):
    state: GameState
    players: list[PlayerData]
    table: list[CardOnTableData]
    hand: list[PunchlineData]
    setup: SetupData | None
    timeout: int | None
    lead_uuid: str | None
    owner_uuid: str
    self_uuid: str | None
    turn_count: int | None
    selected_card: PunchlineData | None = None


class ConnectResponse(ApiModel):
    host: str
    player_token: str
    lobby_token: str


@app.post("/connect")
async def connect(
    *,
    lobby_token: Annotated[str | None, Query(alias="lobbyToken")] = None,
    connect_request: ConnectRequest,
    cards_dao: CardsDAODependency,
) -> ConnectResponse:
    player = Player(
        profile=Profile(
            name=connect_request.name,
            emoji=connect_request.emoji,
        ),
        token=uuid4().hex[:8],
    )
    if lobby_token:
        try:
            lobby = lobbies[lobby_token]
        except KeyError:
            raise HTTPException(status_code=404)
    else:
        lobby = Lobby(
            LobbySettings(winning_score=config.winning_score),
            owner=player,
            setups=await cards_dao.get_setups(deck_id="one"),
            punchlines=await cards_dao.get_punchlines(deck_id="one"),
            state=Gathering(),
        )
        lobby_token = uuid4().hex[:8]
        lobbies[lobby_token] = lobby
        print(f"Lobby created. lobbies={lobbies}")

    try:
        lobby.add_player(player)
    except GameAlreadyStartedError:
        raise HTTPException(status_code=403)

    player_by_token[player.token] = player
    remove_player_tasks[player.token] = asyncio.create_task(
        run_remove_player(lobby, player, lobby_token, player.token)
    )
    return ConnectResponse(
        host=config.ws_url,
        player_token=player.token,
        lobby_token=lobby_token,
    )


@app.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    player_token: Annotated[str, Query(alias="playerToken")],
    lobby_token: Annotated[str, Query(alias="lobbyToken")],
    cards_dao: CardsDAODependency,
):
    await websocket.accept()
    try:
        lobby = lobbies[lobby_token]
    except KeyError:
        await websocket.send_json(
            {"type": "error", "data": {"status": 404, "message": "Lobby not found"}}
        )
        await websocket.close()
        return

    try:
        player = player_by_token[player_token]
        remote_player = RemotePlayer(websocket=websocket, lobby=lobby, player=player)
        player.connect(remote_player)
    except (KeyError, UnknownPlayerError):
        await websocket.send_json(
            {"type": "error", "data": {"status": 404, "message": "Player not found"}}
        )
        await websocket.close()
        return

    if player_token in remove_player_tasks:
        task = remove_player_tasks.pop(player_token)
        task.cancel()

    send_events_task = asyncio.create_task(remote_player.send_events())

    while True:
        try:
            json_data = await websocket.receive_json()
            print(f"Received event: {json_data}")
            await remote_player.handle_event(json_data, cards_dao=cards_dao)
        except WebSocketDisconnect:
            send_events_task.cancel()
            player.disconnect()
            print("before remove")
            remove_player_tasks[player_token] = asyncio.create_task(
                run_remove_player(lobby, player, lobby_token, player_token)
            )
            break
        except Exception:
            print(f"Unexpected error: {traceback.format_exc()}")


async def run_remove_player(lobby, player, lobby_token, player_token):
    print(f"Player removal scheduled, player_token={player_token}")
    await asyncio.sleep(config.player_removal_delay)
    lobby.remove_player(player)
    if not lobby.all_players:
        del lobbies[lobby_token]
        print(f"Lobby deleted. lobbies={lobbies}")


def is_card_picked(lobby: Lobby, card_on_table):
    return (
        card_on_table.player is lobby.state.winner
        if isinstance(lobby.state, Judgement)
        else False
    )


@app.get("/changelog")
async def changelog(
    async_session: SessionDependency,
    version: Annotated[str | None, Query(alias="version")] = None,
):
    async with async_session() as session:
        query = select(Changelog.version).order_by(Changelog.id.desc()).limit(1)
        result = await session.execute(query)
        current_version = result.first()[0]

    if not version:
        return ChangelogResponse(
            changelog=[],
            current_version=current_version,
        )

    subquery_clause = (
        select(Changelog.id)
        .where(Changelog.version == version)
        .order_by(Changelog.id.desc())
        .limit(1)
    )
    subquery = subquery_clause.subquery()

    query = select(Changelog.version, Changelog.text).where(
        Changelog.id > subquery.c.id
    )

    async with async_session() as session:
        result = await session.execute(query)
    records = result.all()

    return ChangelogResponse(
        changelog=[
            ChangelogData(version=record[0], text=record[1]) for record in records
        ],
        current_version=current_version,
    )


@app.get("/")
def health() -> str:
    return "200"
