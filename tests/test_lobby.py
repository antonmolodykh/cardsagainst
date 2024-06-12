import asyncio
from unittest.mock import ANY, Mock, call
from dataclasses import replace
import pytest

from cardsagainst.lobby import (
    CardNotInPlayerHandError,
    Deck,
    Judgement,
    Lobby,
    LobbyObserver,
    LobbySettings,
    NotAllCardsOpenedError,
    Player,
    PlayerNotLeadError,
    PlayerNotOwnerError,
    PunchlineCard,
    SetupCard,
    Turns,
    PlayerAlreadyReadyError,
    ScoreTooLowError,
)


@pytest.mark.usefixtures("egor_connected")
async def test_start_game_set_lead(
    lobby: Lobby,
    egor: Player,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    lobby_settings: LobbySettings,
) -> None:
    egor.start_game(lobby_settings, setup_deck, punchline_deck)
    assert lobby.lead is egor


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_make_turn(
    lobby: Lobby, egor: Player, anton: Player, outbox: Mock
) -> None:
    punchline = anton.hand[0]
    card_on_table = anton.make_turn(punchline)

    assert card_on_table.card is punchline
    assert card_on_table.player is anton
    assert not card_on_table.is_open
    assert punchline not in anton.hand

    expected_events = [
        call.egor.player_ready(anton),
        call.anton.player_ready(anton),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
def test_make_turn_card_not_in_player_hand(egor: Player, anton: Player) -> None:
    with pytest.raises(CardNotInPlayerHandError):
        anton.make_turn(egor.hand[0])


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
def test_open_table_card(egor: Player, anton: Player, outbox: Mock) -> None:
    card_on_table = anton.make_turn(anton.hand[0])

    egor.open_table_card(card_on_table)
    assert card_on_table.is_open

    expected_events = [
        call.egor.table_card_opened(card_on_table),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "anton_joined", "game_started")
def test_open_table_card_player_not_lead(egor: Player, anton: Player) -> None:
    card_on_table = anton.make_turn(anton.hand[0])
    with pytest.raises(PlayerNotLeadError):
        anton.open_table_card(card_on_table)


@pytest.mark.usefixtures(
    "egor_connected", "anton_connected", "yura_connected", "game_started"
)
def test_all_players_ready(
    egor: Player, anton: Player, yura: Player, outbox: Mock
) -> None:
    anton.make_turn(anton.hand[0])
    yura.make_turn(yura.hand[0])
    expected_events = [
        call.egor.all_players_ready(),
        call.anton.all_players_ready(),
        call.yura.all_players_ready(),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_pick_turn_winner(egor: Player, anton: Player, outbox: Mock) -> None:
    punchline = anton.hand[0]
    card_on_table = anton.make_turn(punchline)
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)

    assert anton.score == 1

    expected_events = [
        call.egor.turn_ended(anton, punchline),
        call.anton.turn_ended(anton, punchline),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_pick_turn_winner_not_all_cards_opened(
    lobby: Lobby, egor: Player, anton: Player
) -> None:
    card_on_table = anton.make_turn(anton.hand[0])
    with pytest.raises(NotAllCardsOpenedError):
        egor.pick_turn_winner(card_on_table.card)


@pytest.mark.usefixtures("egor_connected")
def test_add_player(lobby: Lobby, yura: Player, outbox: Mock) -> None:
    lobby.add_player(yura)

    expected_events = [
        call.egor.player_joined(yura),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_joined")
def test_connect_player(lobby: Lobby, yura: Player, outbox: Mock) -> None:
    player_mock = Mock(LobbyObserver)
    outbox.attach_mock(player_mock, "yura")
    yura.connect(player_mock)

    expected_events = [
        call.egor.player_connected(yura),
        call.yura.welcome(),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_disconnect_player(lobby: Lobby, yura: Player, outbox: Mock) -> None:
    yura.disconnect()

    expected_events = [
        call.egor.player_disconnected(yura),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_start_game(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    outbox: Mock,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
    lobby_settings: LobbySettings,
) -> None:
    egor.start_game(lobby_settings, setup_deck, punchline_deck)

    assert isinstance(lobby.state, Turns)

    expected_events = [
        call.game_started(),
        call.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby_settings.turn_duration,
            lead=egor,
            turn_count=1,
        ),
    ]
    outbox.egor.assert_has_calls(expected_events)

    expected_events = [
        call.game_started(),
        call.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby_settings.turn_duration,
            lead=egor,
            turn_count=1,
        ),
    ]
    outbox.yura.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_start_game_player_not_owner_error(
    yura: Player,
    outbox: Mock,
    lobby_settings: LobbySettings,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
) -> None:
    with pytest.raises(PlayerNotOwnerError):
        yura.start_game(lobby_settings, setup_deck, punchline_deck)

    outbox.egor.game_started.assert_not_called()
    outbox.yura.game_started.assert_not_called()


@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_finish_game(egor: Player, yura: Player, outbox: Mock) -> None:
    card_on_table = yura.make_turn(yura.hand[0])
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)

    expected_events = [
        call.egor.game_finished(yura),
        call.yura.game_finished(yura),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_continue_game(
    lobby: Lobby, egor: Player, yura: Player, outbox: Mock
) -> None:
    card_on_table = yura.make_turn(yura.hand[0])
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)

    egor.continue_game()

    assert isinstance(lobby.state, Turns)
    assert lobby.game  # TODO: Do something with it

    expected_events = [
        call.egor.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby.game.settings.turn_duration,
            lead=yura,
            turn_count=2,
        ),
        call.yura.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby.game.settings.turn_duration,
            lead=yura,
            turn_count=2,
            card=ANY,
        ),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_continue_game_player_not_owner(
    lobby: Lobby, egor: Player, yura: Player, outbox: Mock
) -> None:
    card_on_table = yura.make_turn(yura.hand[0])
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)

    with pytest.raises(PlayerNotOwnerError):
        yura.continue_game()


@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_continue_game_no_more_winner(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    outbox: Mock,
    lobby_settings: LobbySettings,
) -> None:
    egor.score = lobby_settings.winning_score - 1
    yura.score = lobby_settings.winning_score - 1

    card_on_table = yura.make_turn(yura.hand[0])
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)
    egor.continue_game()

    assert isinstance(lobby.state, Turns)
    card_on_table = egor.make_turn(egor.hand[0])
    yura.open_table_card(card_on_table)
    yura.pick_turn_winner(card_on_table.card)

    await asyncio.sleep(0.01)

    assert egor.score == lobby_settings.winning_score
    assert isinstance(lobby.state, Turns)


@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_start_game_after_finish(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    outbox: Mock,
    lobby_settings: LobbySettings,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
) -> None:
    card_on_table = yura.make_turn(yura.hand[0])
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)

    lobby_settings.turn_duration = 10
    egor.start_game(lobby_settings, setup_deck, punchline_deck)

    assert isinstance(lobby.state, Turns)

    expected_events = [
        call.game_started(),
        call.turn_started(
            setup=lobby.state.setup,
            turn_duration=10,
            lead=yura,
            turn_count=1,
        ),
    ]
    outbox.egor.assert_has_calls(expected_events)

    expected_events = [
        call.game_started(),
        call.turn_started(
            setup=lobby.state.setup,
            turn_duration=10,
            lead=yura,
            turn_count=1,
        ),
    ]
    outbox.yura.assert_has_calls(expected_events)


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
def test_not_ready_player_removed(lobby: Lobby, anton: Player, yura: Player) -> None:
    yura.make_turn(yura.hand[0])
    lobby.remove_player(anton)
    assert isinstance(lobby.state, Judgement)


@pytest.mark.xfail(reason="Не понятно, что делать если все игроки удалились")
@pytest.mark.usefixtures("egor_connected", "yura_connected", "game_started")
async def test_all_players_removed(lobby: Lobby, egor: Player, yura: Player) -> None:
    lobby.remove_player(egor)
    lobby.remove_player(yura)
    # FIXME: Что делать, если из лобби удалились все игроки?
    #   Сейчас мы пытаемся идти голосовать, но это не реализовано


@pytest.mark.usefixtures("yura_connected", "egor_connected", "game_started")
async def test_owner_removed(
    lobby: Lobby, egor: Player, yura: Player, outbox: Mock
) -> None:
    egor.disconnect()
    assert lobby.owner is egor
    lobby.remove_player(egor)
    assert lobby.owner is yura
    expected_events = [
        call.yura.owner_changed(yura),
    ]
    outbox.assert_has_calls(expected_events)


@pytest.mark.usefixtures("yura_connected", "egor_connected", "game_started")
async def test_resurrect(
    lobby: Lobby, egor: Player, yura: Player, outbox: Mock
) -> None:
    yura.disconnect()
    assert yura in lobby.all_players
    lobby.remove_player(yura)
    assert yura not in lobby.all_players
    assert yura in lobby.grave

    yura.connect(outbox.yura)

    expected_events = [
        call.yura.welcome(),
        call.egor.player_joined(yura),
        call.egor.player_connected(yura),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("yura_connected", "egor_connected", "game_started")
async def test_anton_disconnected_makes_choice(
    lobby: Lobby, egor: Player, yura: Player, anton: Player
) -> None:
    first_choice = yura.hand[0]
    yura.make_turn(first_choice)
    second_choice = yura.hand[0]
    yura.make_turn(second_choice)
    try:
        anton.make_turn(anton.hand[0])
    except IndexError:
        pytest.skip("Почему отключенный Антон не имеет карт в руке?")


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
async def test_make_multiple_choice(
    lobby: Lobby, egor: Player, yura: Player, anton: Player
) -> None:
    first_choice = yura.hand[0]
    yura.make_turn(first_choice)
    second_choice = yura.hand[0]
    yura.make_turn(second_choice)
    anton.make_turn(anton.hand[0])
    assert isinstance(lobby.state, Judgement)
    assert lobby.card_on_table_of(yura).card is second_choice
    assert first_choice in yura.hand


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
async def test_refresh_hand(
    lobby: Lobby, egor: Player, yura: Player, anton: Player, outbox: Mock
) -> None:
    yura.score = 0
    prev_hand = yura.hand.copy()
    yura.refresh_hand()
    expected_events = [
        call.yura.hand_refreshed(yura.hand),
        call.yura.player_score_changed(yura),
        call.egor.player_score_changed(yura),
        call.anton.player_score_changed(yura),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)
    assert prev_hand != yura.hand
    # TODO: Configure min score
    assert yura.score == -1


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
async def test_refresh_hand_decrease_score(
    lobby: Lobby, egor: Player, yura: Player, anton: Player, outbox: Mock
) -> None:
    yura.score = 4
    yura.refresh_hand()
    expected_events = [
        call.egor.player_score_changed(yura),
        call.anton.player_score_changed(yura),
    ]
    outbox.assert_has_calls(expected_events, any_order=True)
    assert yura.score == 3


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
async def test_refresh_hand_score_too_low(
    lobby: Lobby, egor: Player, yura: Player, anton: Player, outbox: Mock
) -> None:
    yura.score = -1
    with pytest.raises(ScoreTooLowError):
        yura.refresh_hand()


@pytest.mark.usefixtures(
    "egor_connected", "yura_connected", "anton_connected", "game_started"
)
async def test_refresh_hand_already_ready(
    lobby: Lobby, egor: Player, yura: Player, anton: Player, outbox: Mock
) -> None:
    yura.make_turn(yura.hand[0])
    prev_hand = yura.hand.copy()
    with pytest.raises(PlayerAlreadyReadyError):
        yura.refresh_hand()
    assert yura.hand == prev_hand


@pytest.mark.skip("Until voting implemented.")
@pytest.mark.usefixtures("egor_connected", "game_started")
async def test_owner_is_unset_if_all_players_left(
    lobby: Lobby, egor: Player, outbox: Mock
) -> None:
    lobby.disconnect(egor)
    lobby.remove_player(egor)
    assert not lobby.owner
    lobby.connect(egor)
    assert egor is lobby.owner
