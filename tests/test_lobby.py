from unittest.mock import Mock, call

import pytest

from lobby import (
    Judgement,
    Deck,
    Lobby,
    LobbyObserver,
    LobbySettings,
    Player,
    PlayerNotDealerError,
    PlayerNotOwnerError,
    CardNotInPlayerHandError,
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
def lobby(
    egor: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> Lobby:
    return Lobby(
        players=[],
        lead=egor,
        owner=egor,
        setups=setup_deck,
        punchlines=punchline_deck,
    )


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


@pytest.mark.usefixtures("anton_joined", "yura_joined")
def test_lobby_change_lead(
    lobby: Lobby, egor: Player, anton: Player, yura: Player
) -> None:
    assert lobby.players == [anton, yura]
    lobby.change_lead()
    assert lobby.players == [yura, egor]
    assert lobby.lead is anton


def test_lobby_change_setup_card(lobby: Lobby, setup_deck: Deck[SetupCard]) -> None:
    setup_card = setup_deck.get_card()
    lobby.change_setup_card(setup_card)
    assert lobby.setup_card is setup_card


@pytest.mark.usefixtures("anton_joined")
def test_lobby_choose_punchline_card(
    lobby: Lobby, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    # TODO: Maybe move this method to player?

    lobby.choose_punchline_card(anton, punchline_card)

    card_on_table = lobby.get_card_from_table(punchline_card)
    assert card_on_table.card is punchline_card
    assert card_on_table.player is anton
    assert not card_on_table.is_open
    assert punchline_card not in anton.hand


@pytest.mark.usefixtures("anton_joined")
def test_lobby_choose_punchline_card_not_in_player_hand(
    lobby: Lobby, egor: Player, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    punchline_card = punchline_deck.get_card()
    egor.hand.append(punchline_card)
    with pytest.raises(CardNotInPlayerHandError):
        lobby.choose_punchline_card(anton, punchline_card)


@pytest.mark.usefixtures("egor_connected", "anton_connected")
def test_open_punchline_card(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)

    # TODO: Return from `choose_punchline_card`
    lobby.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)
    card_on_table = lobby.get_card_from_table(punchline_card)
    lobby.state.open_punchline_card(egor, card_on_table)
    assert card_on_table.is_open

    expected_events = [
        observer.egor.table_card_opened(card_on_table),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("anton_joined")
def test_open_punchline_card_member_not_lead(
    lobby: Lobby, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    punchline_card = punchline_deck.get_card()
    # TODO: Use `Lead` instead of `Dealer`
    with pytest.raises(PlayerNotDealerError):
        lobby.open_punchline_card(anton, punchline_card)


@pytest.mark.usefixtures("anton_joined")
def test_lobby_all_players_ready(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)

    expected_events = [
        observer.egor.all_players_ready(),
        observer.yura.all_players_ready(),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("anton_joined")
def test_lobby_lead_choose_punchline_card(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    assert isinstance(lobby.state, Judgement)
    lobby.state.open_punchline_card(egor, lobby.get_card_from_table(punchline_card))
    expected_events = [
        observer.egor.table_card_opened(lobby.get_card_from_table(punchline_card)),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("anton_joined")
def test_judgement_turn_ended(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.choose_punchline_card(anton, punchline_card)
    lobby.open_punchline_card(egor, punchline_card)

    lobby.lead_choose_punchline_card(punchline_card)

    assert anton.score == 1

    expected_events = [
        observer.egor.turn_ended(anton, punchline_card),
        observer.anton.turn_ended(anton, punchline_card),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected")
def test_player_joined(lobby: Lobby, yura: Player, observer: Mock) -> None:
    lobby.add_player(yura)

    expected_events = [
        call.egor.player_joined(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_joined")
def test_player_connected(lobby: Lobby, yura: Player, observer: Mock) -> None:
    lobby.set_connected(yura)

    expected_events = [
        call.egor.player_connected(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_player_disconnected(lobby: Lobby, yura: Player, observer: Mock) -> None:
    lobby.set_disconnected(yura)

    expected_events = [
        call.egor.player_disconnected(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_owner_start_game(lobby: Lobby, egor: Player, observer: Mock) -> None:
    lobby_settings = LobbySettings(turn_duration=30)
    lobby.start_game(egor, lobby_settings)

    expected_events = [
        call.egor.turn_started(turn_duration=lobby_settings.turn_duration, leed=egor),
        call.yura.turn_started(turn_duration=lobby_settings.turn_duration, leed=egor),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_not_owner_start_game(lobby: Lobby, yura: Player, observer: Mock) -> None:
    lobby_settings = LobbySettings(turn_duration=30)
    with pytest.raises(PlayerNotOwnerError):
        lobby.start_game(yura, lobby_settings)

    observer.egor.turn_started.assert_not_called()
    observer.yura.turn_started.assert_not_called()
