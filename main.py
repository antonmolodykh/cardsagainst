from __future__ import annotations

import asyncio
import traceback
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import uuid4

from fastapi import FastAPI, WebSocket, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import text
from starlette.websockets import WebSocketDisconnect
from typing_extensions import Annotated

from fastapi.middleware.cors import CORSMiddleware

from dao import cards_dao
from db import engine
from lobby import (
    Lobby,
    Player,
    Profile,
    Deck,
    SetupCard,
    PunchlineCard,
    LobbyObserver,
    LobbySettings,
    CardOnTable,
    Judgement,
    Turns,
    Gathering,
)
from models import metadata

lobby: Lobby = None
observers: list[LobbyObserver] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

players: dict[str, Player] = {}


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


def get_player_data_from_player(player: Player) -> PlayerData:
    return PlayerData(
        uuid=player.uuid,
        name=player.profile.name,
        emoji=player.profile.emoji,
        background_color=player.profile.background_color,
        state=PlayerState.PENDING,
        score=player.score,
        is_lobby_owner=lobby.owner is player,
        is_connected=player.is_connected,
    )


queue = asyncio.Queue()


async def send_messages():
    while True:
        event = await queue.get()


class PlayerIdData(ApiModel):
    uuid: str


class SetupData(ApiModel):
    uuid: str
    text: str
    case: str
    starts_with_punchline: bool

    @classmethod
    def from_setup(cls, setup: SetupCard):
        return cls(
            uuid=str(setup.id),
            text=setup.text,
            case=setup.case,
            starts_with_punchline=setup.starts_with_punchline,
        )


class PunchlineData(ApiModel):
    uuid: str
    text: list[tuple[str, list[str]]]

    @classmethod
    def from_card(cls, card: PunchlineCard):
        return cls(uuid=str(card.id), text=card.text)


class CardOnTableData(ApiModel):
    card: PunchlineData | None
    is_picked: bool
    author: str | None


class TableCardOpenedData(ApiModel):
    index: int
    card: PunchlineData


class TurnEndedData(ApiModel):
    winner_uuid: str
    card_uuid: str
    score: int


class GameFinishedData(ApiModel):
    winner_uuid: str


class GameStartedData(ApiModel):
    hand: list[PunchlineData]


class RemotePlayer(LobbyObserver):
    def __init__(self, websocket: WebSocket, player: Player, lobby: Lobby) -> None:
        self.lobby = lobby
        self.player = player
        self.websocket = websocket
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
                    timeout=turn_duration,
                    lead_uuid=lead.uuid,
                    turn_count=turn_count,
                    is_leading=self.player is lead,
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
                    winner_uuid=winner.uuid, card_uuid=str(card.id), score=winner.score
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

    async def send_messages(self):
        while True:
            event = await self._queue.get()
            data = event.model_dump(by_alias=True)
            print(f"Event: {data}")
            await self.websocket.send_json(data)


class ConnectRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    name: str
    emoji: str
    background_color: str


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
    background_color: str
    state: PlayerState
    score: int
    is_lobby_owner: bool
    is_connected: bool


AnyEventData = TypeVar("AnyEventData", bound=ApiModel)


class Event(ApiModel, Generic[AnyEventData]):
    id: int
    type: str
    data: AnyEventData | None


class StartGameData(ApiModel):
    timeout: int | None


class MakeTurnData(ApiModel):
    uuid: str


class OpenTableCardData(ApiModel):
    index: int


class PickTurnWinnerData(ApiModel):
    uuid: str


class TurnStartedData(ApiModel):
    setup: SetupData
    timeout: int | None
    lead_uuid: str
    is_leading: bool
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
    is_leading: bool
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
) -> ConnectResponse:
    global lobby

    if not lobby_token and lobby:
        raise HTTPException(status_code=403)

    if not lobby and lobby_token:
        raise HTTPException(status_code=404)

    player = Player(
        profile=Profile(
            name=connect_request.name,
            emoji=connect_request.emoji,
            background_color=connect_request.background_color,
        ),
    )
    player_token = uuid4().hex
    players[player_token] = player
    if lobby_token:
        lobby.add_player(player)
    else:
        setups = await cards_dao.get_setups(deck_id="one")
        punchlines = await cards_dao.get_punchlines(deck_id="one")

        lobby = Lobby(
            players=[],
            lead=player,
            owner=player,
            setups=setups,
            punchlines=punchlines,
            state=Gathering(),
        )
    return ConnectResponse(
        host="ws://192.168.0.18:9999/connect",
        player_token=player_token,
        lobby_token="boba",
    )


@app.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    player_token: Annotated[str, Query(alias="playerToken")],
    lobby_token: Annotated[str, Query(alias="lobbyToken")],
):
    await websocket.accept()

    try:
        player = players[player_token]
    except KeyError:
        raise HTTPException(status_code=404)
    # TODO пренадлежность к лобби

    observer = RemotePlayer(websocket=websocket, lobby=lobby, player=player)
    send_messages_task = asyncio.create_task(observer.send_messages())
    player.observer = observer

    lobby.set_connected(player)
    selected_card = lobby.get_selected_card(player)
    await websocket.send_json(
        Event(
            id=1,
            type="welcome",
            data=LobbyState(
                state=GameState(type(lobby.state).__name__.lower()),
                turn_count=lobby.turn_count,
                players=[
                    get_player_data_from_player(player)
                    for player in (*lobby.players, lobby.lead)
                ],
                table=[
                    CardOnTableData(
                        card=card_on_table.card if card_on_table.is_open else None,
                        is_picked=is_card_picked(card_on_table),
                        author=(
                            card_on_table.player.profile.name
                            if is_card_picked(card_on_table)
                            else None
                        ),
                    )
                    for card_on_table in lobby.table
                ],
                hand=[PunchlineData.from_card(item) for item in player.hand],
                setup=(
                    SetupData.from_setup(lobby.state.setup)
                    if isinstance(lobby.state, Judgement | Turns)
                    else None
                ),
                timeout=lobby.settings.turn_duration,
                lead_uuid=lobby.lead.uuid,
                is_leading=player is lobby.lead,
                selected_card=(
                    PunchlineData.from_card(selected_card) if selected_card else None
                ),
            ),
        ).model_dump(by_alias=True)
    )

    while True:
        try:
            json_data = await websocket.receive_json()
            print(f"Received event: {json_data}")
            await handle_event(json_data, player)
        except WebSocketDisconnect:
            send_messages_task.cancel()
            lobby.set_disconnected(player)
            break
        except Exception:
            print(f"Unexpected error: {traceback.format_exc()}")


def is_card_picked(card_on_table):
    return (
        card_on_table.player is lobby.state.winner
        if isinstance(lobby.state, Judgement)
        else False
    )


async def handle_event(json_data, player) -> None:
    match json_data["type"]:
        case "startGame":
            event = Event[StartGameData].model_validate(json_data)
            lobby.state.start_game(
                player=player,
                lobby_settings=LobbySettings(turn_duration=event.data.timeout),
            )
        case "makeTurn":
            event = Event[MakeTurnData].model_validate(json_data)
            try:
                card = lobby.punchlines.get_card_by_uuid(int(event.data.uuid))
            except KeyError:
                print("unknown card")
                return
            lobby.state.choose_punchline_card(player, card)
        case "openTableCard":
            event = Event[OpenTableCardData].model_validate(json_data)
            lobby.state.open_punchline_card(player, lobby.table[event.data.index])
        case "pickTurnWinner":
            event = Event[PickTurnWinnerData].model_validate(json_data)
            try:
                card = lobby.punchlines.get_card_by_uuid(int(event.data.uuid))
            except KeyError:
                return
            lobby.state.pick_turn_winner(card)


@app.get("/")
def health() -> str:
    return "200"


@app.on_event("startup")
async def startup() -> None:
    """Init DB tables and sequences"""
    async with engine.begin() as conn:
        # Create tables if not exist
        await conn.run_sync(metadata.create_all)
