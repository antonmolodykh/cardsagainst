from unittest.mock import Mock, call, ANY

import pytest

from lobby import (
    CardOnTable,
    Deck,
    Lobby,
    LobbyObserver,
    Player,
    PlayerNotDealerError,
    PlayerNotPunchlineCardHolderError,
    Profile,
    PunchlineCard,
    SetupCard, LobbySettings, PlayerNotOwnerError
)


@pytest.fixture
def setup_card() -> SetupCard:
    return SetupCard()


@pytest.fixture
def punchline_card() -> PunchlineCard:
    return PunchlineCard()


@pytest.fixture
def setup_cards_deck(setup_card: SetupCard) -> Deck[SetupCard]:
    return Deck(cards=[setup_card])


@pytest.fixture
def punchline_cards_deck(punchline_card: PunchlineCard) -> Deck[PunchlineCard]:
    return Deck(cards=[punchline_card])


def test_deck_get_random_card(
    setup_cards_deck: Deck[SetupCard], setup_card: SetupCard
) -> None:
    assert setup_cards_deck.get_card() is setup_card


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
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        players=[egor, anton],
        lead=yura,
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    lobby.change_lead()
    assert lobby.players == [anton, yura]
    assert lobby.lead is egor


def test_lobby_change_setup_card(
    egor: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    new_setup_card = SetupCard()
    setup_cards_deck.cards.append(new_setup_card)
    lobby.change_setup_card(new_setup_card)
    assert lobby.setup_card is new_setup_card


def test_lobby_choose_punchline_card(
    egor: Player,
    anton: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[anton],
        owner=anton,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_cards_deck.get_card()
    anton.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    assert punchline_card is lobby.get_card_from_table(punchline_card).card
    assert punchline_card not in anton.punchline_cards


def test_lobby_choose_punchline_member_not_punchline_holder(
    egor: Player,
    anton: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_cards_deck.get_card()
    egor.punchline_cards.append(punchline_card)
    with pytest.raises(PlayerNotPunchlineCardHolderError):
        lobby.choose_punchline_card(anton, punchline_card)


def test_open_punchline_card(
    egor: Player,
    anton: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[anton],
        owner=anton,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_cards_deck.get_card()
    anton.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    lobby.open_punchline_card(egor, punchline_card)
    assert isinstance(lobby.table[0], CardOnTable)


def test_open_punchline_card_member_not_lead(
    egor: Player,
    anton: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = PunchlineCard()
    with pytest.raises(PlayerNotDealerError):
        lobby.open_punchline_card(egor, punchline_card)


def test_lobby_lead_choose_punchline_card(
    egor: Player,
    anton: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: LobbyObserver,
) -> None:
    lobby = Lobby(
        lead=anton,
        players=[egor],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,  # FIXME: It's annoying to provide it every time
    )
    punchline_card = punchline_cards_deck.get_card()
    egor.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(egor, punchline_card)
    lobby.open_punchline_card(anton, punchline_card)
    lobby.lead_choose_punchline_card(punchline_card)
    assert egor.score == 1


@pytest.mark.usefixtures("egor connected")
def test_player_joined(
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    egor: Player,
    yura: Player,
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
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
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    egor: Player,
    yura: Player,
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
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
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,
    )
    lobby.add_player(yura)
    lobby.set_connected(yura)

    lobby.set_disconnected(yura)


@pytest.mark.usefixtures("egor connected", "yura connected")
def test_player_disconnected(
    egor: Player,
    yura: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,
    )
    lobby.add_player(yura)
    lobby.set_connected(yura)

    lobby.set_disconnected(yura)

    expected_events = [
        call.egor.player_disconnected(yura),
    ]
    observer.assert_has_calls(expected_events)


def test_player_connected(
    egor: Player,
    yura: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    egor_mock = Mock()
    egor = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=egor_mock,
    )

    yura_mock = Mock()
    yura = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=yura_mock,
    )

    observer.attach_mock(yura_mock, "yura")
    observer.attach_mock(egor_mock, "egor")

    # FIXME: Lobby is not used. Looks like lobby must be required to send events
    lobby = Lobby(
        lead=egor,
        players=[yura],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,
    )
    # FIXME: I want to test which player has received the message

    lobby.set_connected(yura)

    expected_events = [
        call.egor.player_connected(yura),
    ]
    observer.assert_has_calls(expected_events)


def test_owner_start_game(
    egor: Player,
    yura: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    egor_mock = Mock()
    egor = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=egor_mock,
    )

    observer.attach_mock(egor_mock, "egor")

    lobby = Lobby(
        lead=egor,
        players=[],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,
    )

    lobby_settings = LobbySettings(turn_duration=30)
    lobby.start_game(egor, lobby_settings)

    expected_events = [
        call.egor.turn_started(turn_duration=lobby_settings.turn_duration),
    ]
    observer.assert_has_calls(expected_events)


def test_not_owner_start_game(
    egor: Player,
    yura: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    egor_mock = Mock()
    egor = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=egor_mock,
    )

    yura_mock = Mock()
    yura = Player(
        profile=Profile(name="yura", emoji="🍎", background_color="#ff0000"),
        observer=yura_mock,
    )

    lobby = Lobby(
        lead=egor,
        players=[yura],
        owner=egor,
        setups=setup_cards_deck,
        punchlines=punchline_cards_deck,
        observer=observer,
    )

    lobby_settings = LobbySettings(turn_duration=30)
    with pytest.raises(PlayerNotOwnerError):
        lobby.start_game(yura, lobby_settings)

    unexpected_events = [
        call.egor.turn_started(ANY),
        call.yura.turn_started(ANY),
    ]
    assert not any(event in observer.mock_calls for event in unexpected_events)
