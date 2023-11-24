from unittest.mock import Mock

import pytest

from lobby import Deck, Lobby, LobbyObserver, Player, Profile, PunchlineCard, SetupCard


@pytest.fixture
def setup_deck_size() -> int:
    return 10


@pytest.fixture
def setup_deck(setup_deck_size: int) -> Deck[SetupCard]:
    return Deck(
        cards=[
            SetupCard(text="", case="", starts_with_punchline=False)
            for _ in range(setup_deck_size)
        ]
    )


@pytest.fixture
def punchline_deck_size() -> int:
    # TODO: I want to control the "hand size"
    return 100


@pytest.fixture
def punchline_deck(punchline_deck_size: int) -> Deck[PunchlineCard]:
    return Deck(
        cards=[PunchlineCard(text={"a": "b"}) for _ in range(punchline_deck_size)]
    )


@pytest.fixture
def observer() -> Mock:
    return Mock(LobbyObserver)


@pytest.fixture
def egor() -> Player:
    return Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
    )


@pytest.fixture
def anton() -> Player:
    return Player(
        profile=Profile(name="anton", emoji="🍎", background_color="#ff0000"),
    )


@pytest.fixture
def yura() -> Player:
    return Player(
        profile=Profile(name="yura", emoji="🍎", background_color="#ff0000"),
    )


@pytest.fixture
def state_gathering() -> Gathering:
    return Gathering()


@pytest.fixture
def lobby(
    egor: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
    state_gathering: Gathering,
) -> Lobby:
    lobby = Lobby(
        players=[],
        lead=egor,
        owner=egor,
        state=state_gathering,
        # TODO: state gathering determines the setups and punchlines
        # Move?
        setups=setup_deck,
        punchlines=punchline_deck,
    )
    return lobby


@pytest.fixture
def egor_connected(egor: Player, observer: Mock) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "egor")
    egor.observer = player_mock


@pytest.fixture
def anton_joined(lobby: Lobby, anton: Player) -> None:
    lobby.add_player(anton)


@pytest.fixture
def anton_connected(
    anton_joined: None, lobby: Lobby, anton: Player, observer: Mock
) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "anton")
    anton.observer = player_mock
    lobby.set_connected(anton)


@pytest.fixture
def yura_joined(lobby: Lobby, yura: Player) -> None:
    lobby.add_player(yura)


@pytest.fixture
def yura_connected(
    yura_joined: None, lobby: Lobby, yura: Player, observer: Mock
) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "yura")
    yura.observer = player_mock
    lobby.set_connected(yura)
