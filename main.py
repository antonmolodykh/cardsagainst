from __future__ import annotations

import asyncio
import traceback
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import uuid4

from fastapi import FastAPI, WebSocket, Query, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from starlette.websockets import WebSocketDisconnect
from typing_extensions import Annotated

from fastapi.middleware.cors import CORSMiddleware

from lobby import Lobby, Player, Profile, Deck, SetupCard, PunchlineCard, LobbyObserver

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
        uuid=player.uid,
        name=player.profile.name,
        emoji=player.profile.emoji,
        background_color=player.profile.background_color,
        state=PlayerState.PENDING,
        score=player.score,
        is_lobby_owner=False,
        is_connected=player.is_connected,
    )


queue = asyncio.Queue()


async def send_messages():
    while True:
        event = await queue.get()


class PlayerIdData(ApiModel):
    uuid: str


class BroadcastObserver(LobbyObserver):
    PLAYER_REMOVAL_DELAY: int = 15

    def __init__(self):
        self.websockets = []
        self.queue = asyncio.Queue()

    def add_websocket(self, websocket: WebSocket):
        self.websockets.append(websocket)

    def remove_websocket(self, websocket: WebSocket):
        self.websockets.remove(websocket)

    async def schedule_player_removal(self, player):
        await asyncio.sleep(self.PLAYER_REMOVAL_DELAY)
        if player.is_connected is False:
            lobby.remove_player(player)

    def player_joined(self, player: Player):
        self.queue.put_nowait(
            Event(id=1, type="playerJoined", data=get_player_data_from_player(player))
        )

    def player_left(self, player: Player):
        self.queue.put_nowait(
            Event(id=1, type="playerLeft", data=PlayerIdData(uuid=player.uid))
        )

    def player_connected(self, player: Player):
        self.queue.put_nowait(
            Event(id=2, type="playerConnected", data=PlayerIdData(uuid=player.uid))
        )

    def player_disconnected(self, player: Player):
        self.queue.put_nowait(
            Event(id=1, type="playerDisconnected", data=PlayerIdData(uuid=player.uid))
        )
        asyncio.create_task(self.schedule_player_removal(player))

    async def send_messages(self):
        while True:
            event = await self.queue.get()
            print(f"Event: {event}")
            await asyncio.gather(
                *(
                    websocket.send_json(event.model_dump(by_alias=True))
                    for websocket in self.websockets
                )
            )


broadcast_observer = BroadcastObserver()
asyncio.create_task(broadcast_observer.send_messages())


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
    BEGIN = "begin"
    MOVE = "move"
    JUDGING = "judging"
    END = "end"


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
    data: AnyEventData


class LobbyState(ApiModel):
    state: GameState
    players: list[PlayerData]
    table_cards: list[TableCard] | None = None


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
        observer=broadcast_observer,
    )
    player_token = uuid4().hex
    players[player_token] = player
    if lobby_token:
        lobby.add_player(player)

    else:
        setups = Deck(cards=[SetupCard(), SetupCard(), SetupCard()])
        punchlines = Deck(cards=[PunchlineCard(), PunchlineCard(), PunchlineCard()])

        lobby = Lobby(
            players=[],
            lead=player,
            owner=player,
            setups=setups,
            punchlines=punchlines,
            observer=broadcast_observer,
        )
    return ConnectResponse(
        host="wss://c9gws36c-9999.euw.devtunnels.ms/connect",
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
    # connected_clients.append(websocket)
    player = players[player_token]
    # TODO пренадлежность к лобби

    broadcast_observer.add_websocket(websocket)
    player.set_connected()
    await websocket.send_json(
        Event(
            id=1,
            type="welcome",
            data=LobbyState(
                state=GameState.BEGIN,
                players=[
                    get_player_data_from_player(player)
                    for player in (*lobby.players, lobby.lead)
                ],
                table_cards=None,
            ),
        ).model_dump(by_alias=True)
    )

    while True:
        try:
            data = await websocket.receive_json()
            print(f"Received data: {data}")
        except WebSocketDisconnect:
            broadcast_observer.remove_websocket(websocket)
            player.set_disconnected()
            break
        except Exception:
            print(f"Unexpected error: {traceback.format_exc()}")

    # try:
    #     while True:
    #         message = await websocket.receive_text()
    #         await send_message_to_all(message)
    # except Exception as e:
    #     print(f"Ошибка: {e}")
    # finally:
    #     connected_clients.remove(websocket)


@app.get("/")
def health() -> str:
    return "200"
