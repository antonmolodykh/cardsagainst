import asyncio
from unittest.mock import ANY, Mock, call

import pytest

from lobby import (
    CardNotInPlayerHandError,
    Deck,
    Judgement,
    Lobby,
    LobbySettings,
    Player,
    PlayerNotDealerError,
    PlayerNotOwnerError,
    PunchlineCard,
    SetupCard,
    Turns,
)


@pytest.mark.usefixtures("anton_joined", "yura_joined")
def test_lobby_change_lead(
    lobby: Lobby, egor: Player, anton: Player, yura: Player
) -> None:
    assert lobby.players == [anton, yura]
    lobby.change_lead()
    assert lobby.players == [yura, egor]
    assert lobby.lead is anton


@pytest.mark.usefixtures("egor_connected", "anton_connected")
def test_lobby_choose_punchline_card(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.state.start_game(egor, lobby.settings)

    # TODO: Maybe move this method to player?
    lobby.state.choose_punchline_card(anton, punchline_card)

    card_on_table = lobby.get_card_from_table(punchline_card)
    assert card_on_table.card is punchline_card
    assert card_on_table.player is anton
    assert not card_on_table.is_open
    assert punchline_card not in anton.hand

    expected_events = [
        call.egor.player_ready(anton),
        call.anton.player_ready(anton),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("anton_joined")
def test_lobby_choose_punchline_card_not_in_player_hand(
    lobby: Lobby, egor: Player, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    punchline_card = punchline_deck.get_card()
    egor.hand.append(punchline_card)
    lobby.state.start_game(egor, lobby.settings)
    with pytest.raises(CardNotInPlayerHandError):
        lobby.state.choose_punchline_card(anton, punchline_card)


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
    lobby.state.start_game(egor, lobby.settings)
    lobby.state.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)
    card_on_table = lobby.get_card_from_table(punchline_card)
    lobby.state.open_punchline_card(egor, card_on_table)
    assert card_on_table.is_open

    expected_events = [
        call.egor.table_card_opened(card_on_table),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("anton_joined")
def test_open_punchline_card_member_not_lead(
    lobby: Lobby, egor: Player, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)

    lobby.state.start_game(egor, lobby.settings)
    lobby.state.choose_punchline_card(anton, punchline_card)

    # TODO: Use `Lead` instead of `Dealer`
    with pytest.raises(PlayerNotDealerError):
        assert isinstance(lobby.state, Judgement)
        lobby.state.open_punchline_card(
            anton, lobby.get_card_from_table(punchline_card)
        )


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_lobby_all_players_ready(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.state.start_game(egor, lobby.settings)
    lobby.state.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)

    expected_events = [
        call.egor.all_players_ready(),
        call.yura.all_players_ready(),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "anton_connected")
def test_lobby_lead_choose_punchline_card(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)

    lobby.state.start_game(egor, lobby.settings)
    lobby.state.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)
    lobby.state.open_punchline_card(egor, lobby.get_card_from_table(punchline_card))
    expected_events = [
        call.egor.table_card_opened(lobby.get_card_from_table(punchline_card)),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "anton_connected")
async def test_judgement_turn_ended(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    observer,
) -> None:
    punchline_card = punchline_deck.get_card()
    anton.hand.append(punchline_card)
    lobby.state.start_game(egor, lobby.settings)
    lobby.state.choose_punchline_card(anton, punchline_card)

    assert isinstance(lobby.state, Judgement)
    card_on_table = lobby.get_card_from_table(punchline_card)
    lobby.state.open_punchline_card(egor, card_on_table)

    # TODO: provide `card_on_table`
    lobby.state.pick_turn_winner(card_on_table.card)

    assert anton.score == 1

    expected_events = [
        call.egor.turn_ended(anton, punchline_card),
        call.anton.turn_ended(anton, punchline_card),
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
def test_lead_start_game(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    observer: Mock,
    setup_deck: Deck[SetupCard],
) -> None:
    lobby_settings = LobbySettings(winning_score=1, turn_duration=30)
    lobby.state.start_game(egor, lobby_settings)
    assert isinstance(lobby.state, Turns)
    expected_events = [
        call.egor.game_started(egor),
        call.egor.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby_settings.turn_duration,
            lead=egor,
            turn_count=1,
        ),
        call.yura.game_started(yura),
        call.yura.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby_settings.turn_duration,
            lead=egor,
            turn_count=1,
        ),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
def test_not_owner_start_game(lobby: Lobby, yura: Player, observer: Mock) -> None:
    lobby_settings = LobbySettings(winning_score=1, turn_duration=30)
    with pytest.raises(PlayerNotOwnerError):
        lobby.state.start_game(yura, lobby_settings)

    observer.egor.turn_started.assert_not_called()
    observer.yura.turn_started.assert_not_called()


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_finish_game(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    observer: Mock,
    punchline_deck: Deck[PunchlineCard],
) -> None:
    lobby.state.start_game(egor, LobbySettings(winning_score=1, finish_delay=0))
    punchline_card = punchline_deck.get_card()
    yura.hand.append(punchline_card)
    lobby.state.choose_punchline_card(yura, punchline_card)
    lobby.state.pick_turn_winner(punchline_card)
    await asyncio.sleep(0.01)
    # TODO: Events about finished game

    expected_events = [
        call.egor.game_finished(yura),
        call.yura.game_finished(yura),
    ]
    observer.assert_has_calls(expected_events)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_continue(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    observer: Mock,
    punchline_deck: Deck[PunchlineCard],
) -> None:
    lobby.state.start_game(egor, LobbySettings(winning_score=1, finish_delay=0))
    punchline_card = punchline_deck.get_card()
    yura.hand.append(punchline_card)
    lobby.state.choose_punchline_card(yura, punchline_card)
    lobby.state.pick_turn_winner(punchline_card)
    await asyncio.sleep(0.01)
    lobby.state.continue_game(egor)

    assert isinstance(lobby.state, Turns)

    expected_events = [
        call.egor.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby.settings.turn_duration,
            lead=yura,
            turn_count=2,
        ),
        call.yura.turn_started(
            setup=lobby.state.setup,
            turn_duration=lobby.settings.turn_duration,
            lead=yura,
            turn_count=2,
            card=ANY,
        ),
    ]
    observer.assert_has_calls(expected_events, any_order=True)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_continue_not_owner(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    observer: Mock,
    punchline_deck: Deck[PunchlineCard],
) -> None:
    lobby.state.start_game(egor, LobbySettings(winning_score=1, finish_delay=0))
    punchline_card = punchline_deck.get_card()
    yura.hand.append(punchline_card)
    lobby.state.choose_punchline_card(yura, punchline_card)
    lobby.state.pick_turn_winner(punchline_card)
    await asyncio.sleep(0.01)

    with pytest.raises(PlayerNotOwnerError):
        lobby.state.continue_game(yura)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_start_game_after_finish(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    observer: Mock,
    punchline_deck: Deck[PunchlineCard],
) -> None:
    lobby.state.start_game(egor, LobbySettings(winning_score=1, finish_delay=0))
    punchline_card = punchline_deck.get_card()
    yura.hand.append(punchline_card)
    lobby.state.choose_punchline_card(yura, punchline_card)
    lobby.state.pick_turn_winner(punchline_card)
    await asyncio.sleep(0.01)
    lobby.state.start_game(
        egor, LobbySettings(turn_duration=10, winning_score=2, finish_delay=0)
    )

    assert isinstance(lobby.state, Turns)

    expected_events = [
        call.egor.game_started(egor),
        call.egor.turn_started(
            setup=lobby.state.setup,
            turn_duration=10,
            lead=egor,
            turn_count=1,
        ),
        call.yura.game_started(yura),
        call.yura.turn_started(
            setup=lobby.state.setup,
            turn_duration=10,
            lead=egor,
            turn_count=1,
        ),
    ]
    observer.assert_has_calls(expected_events, any_order=True)
