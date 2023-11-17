from unittest.mock import Mock, call

import pytest

from lobby import (
    CardOnTable,
    Deck,
    Lobby,
    LobbyObserver,
    LobbySettings,
    Player,
    PlayerNotDealerError,
    PlayerNotOwnerError,
    PlayerNotPunchlineCardHolderError,
    Profile,
    PunchlineCard,
    SetupCard,
)


@pytest.fixture
def setup_deck_size() -> int:
    return 10


@pytest.fixture
def setup_deck(setup_deck_size: int) -> Deck[SetupCard]:
    return Deck(
        cards=[
            SetupCard(text="", case="", start_with_punchline=False)
            for _ in range(setup_deck_size)
        ]
    )


@pytest.fixture
def punchline_deck_size() -> int:
    # TODO: I want to control hand size
    return 100


@pytest.fixture
def punchline_deck(punchline_deck_size: int) -> Deck[PunchlineCard]:
    return Deck(
        cards=[PunchlineCard(text={"a": "b"}) for _ in range(punchline_deck_size)]
    )


@pytest.fixture
def observer() -> LobbyObserver:
    return Mock(LobbyObserver)


@pytest.fixture
def egor() -> Player:
    player = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
    )
    return player


@pytest.fixture
def anton() -> Player:
    player = Player(
        profile=Profile(name="anton", emoji="🍎", background_color="#ff0000"),
    )
    return player


@pytest.fixture
def yura() -> Player:
    return Player(
        profile=Profile(name="yura", emoji="🍎", background_color="#ff0000"),
    )


@pytest.fixture(name="egor connected")
def egor_connected(egor: Player, observer: Mock) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "egor")
    egor.observer = player_mock


@pytest.fixture(name="anton connected")
def anton_connected(anton: Player, observer: Mock) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "anton")
    anton.observer = player_mock


@pytest.fixture(name="yura connected")
def yura_connected(yura: Player, observer: Mock) -> None:
    player_mock = Mock(LobbyObserver)
    observer.attach_mock(player_mock, "yura")
    yura.observer = player_mock


def test_lobby_change_lead(
    egor: Player,
    anton: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        players=[egor, anton],
        lead=yura,
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: Looks like it's redundant
    )
    lobby.change_lead()
    assert lobby.players == [anton, yura]
    assert lobby.lead is egor


def test_lobby_change_setup_card(
    egor: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: Looks like it's redundant
    )
    new_setup_card = SetupCard(
        text="new setup card", case="", start_with_punchline=False
    )
    setup_deck.cards.append(new_setup_card)
    lobby.change_setup_card(new_setup_card)
    assert lobby.setup_card is new_setup_card


def test_lobby_choose_punchline_card(
    egor: Player,
    anton: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[anton],
        owner=anton,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_deck.get_random_card()
    anton.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    assert punchline_card is lobby.get_card_from_table(punchline_card).card
    assert punchline_card not in anton.punchline_cards


def test_lobby_choose_punchline_member_not_punchline_holder(
    egor: Player,
    anton: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_deck.get_random_card()
    egor.punchline_cards.append(punchline_card)
    with pytest.raises(PlayerNotPunchlineCardHolderError):
        lobby.choose_punchline_card(anton, punchline_card)


def test_open_punchline_card(
    egor: Player,
    anton: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[anton],
        owner=anton,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_deck.get_random_card()
    anton.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    lobby.open_punchline_card(egor, punchline_card)
    assert isinstance(lobby.table[0], CardOnTable)


def test_open_punchline_card_member_not_lead(
    egor: Player,
    anton: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_deck.get_random_card()
    with pytest.raises(PlayerNotDealerError):
        lobby.open_punchline_card(egor, punchline_card)


def test_lobby_lead_choose_punchline_card(
    egor: Player,
    anton: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_deck.get_random_card()
    egor.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(egor, punchline_card)
    lobby.open_punchline_card(anton, punchline_card)
    lobby.lead_choose_punchline_card(punchline_card)
    assert egor.score == 1


@pytest.mark.usefixtures("egor connected")
def test_player_joined(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )
    # FIXME: I want to test which player has received the message
    lobby.add_player(yura)

    expected_events = [
        call.egor.player_joined(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("yura connected")
def test_player_not_received_self_joined(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )
    lobby.add_player(yura)

    unexpected_events = [
        call.yura.player_joined(yura),
    ]
    assert not any(event in observer.mock_calls for event in unexpected_events)


@pytest.mark.usefixtures("egor connected", "yura connected")
def test_player_disconnected(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )
    lobby.add_player(yura)
    lobby.set_connected(yura)

    lobby.set_disconnected(yura)


@pytest.mark.usefixtures("egor connected", "yura connected")
def test_player_disconnected(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )
    lobby.add_player(yura)
    lobby.set_connected(yura)

    lobby.set_disconnected(yura)

    expected_events = [
        call.egor.player_disconnected(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor connected")
def test_player_connected(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[yura],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )
    lobby.set_connected(yura)

    expected_events = [
        call.egor.player_connected(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor connected", "yura connected")
def test_owner_start_game(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[yura],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )

    lobby_settings = LobbySettings(turn_duration=30)
    lobby.start_game(egor, lobby_settings)

    expected_events = [
        call.egor.turn_started(turn_duration=lobby_settings.turn_duration),
        call.yura.turn_started(turn_duration=lobby_settings.turn_duration),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor connected", "yura connected")
def test_not_owner_start_game(
    egor: Player,
    yura: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[yura],
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
        observer=observer,
    )

    lobby_settings = LobbySettings(turn_duration=30)
    with pytest.raises(PlayerNotOwnerError):
        lobby.start_game(yura, lobby_settings)

    observer.egor.turn_started.assert_not_called()
    observer.yura.turn_started.assert_not_called()
