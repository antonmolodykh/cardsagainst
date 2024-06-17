import asyncio

import pytest

from cardsagainst.lobby import (
    CardOnTable,
    Deck,
    Finished,
    Judgement,
    Lobby,
    LobbySettings,
    Player,
    PunchlineCard,
    SetupCard,
    Turns,
)


@pytest.mark.usefixtures("egor_connected", "yura_connected")
async def test_start_game_transit_to_turns(
    lobby: Lobby,
    egor: Player,
    yura: Player,
    lobby_settings: LobbySettings,
    setup_deck: Deck[SetupCard],
    punchline_deck: Deck[PunchlineCard],
) -> None:
    egor.start_game(lobby_settings, setup_deck, punchline_deck)
    isinstance(lobby.state, Turns)


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_transit_turns_to_judgement(
    lobby: Lobby,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    setup_deck: Deck[SetupCard],
) -> None:
    assert isinstance(lobby.state, Turns)
    setup_card = lobby.state.setup
    anton.make_turn(anton.hand[0])
    await asyncio.sleep(0.01)
    assert isinstance(lobby.state, Judgement)
    assert lobby.state.setup is setup_card


@pytest.mark.skip("Set game on Gathering")
async def test_transit_judgement_to_turns(
    lobby: Lobby,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    setup_deck: Deck[SetupCard],
) -> None:
    setup_card = setup_deck.get_card()
    next_setup_card = setup_deck.cards[-1]
    lobby.add_player(anton)
    lobby.transit_to(Judgement(setup_card))
    lobby.state.start_turn()
    assert isinstance(lobby.state, Turns)
    assert lobby.state.setup is next_setup_card


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_transit_judgement_to_finished(
    lobby: Lobby,
    egor: Player,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    setup_deck: Deck[SetupCard],
) -> None:
    anton.make_turn(anton.hand[0])
    card_on_table = lobby.table[0]
    egor.open_table_card(card_on_table)
    egor.pick_turn_winner(card_on_table.card)
    await asyncio.sleep(0.01)
    assert isinstance(lobby.state, Finished)


@pytest.mark.usefixtures("egor_connected", "anton_connected", "game_started")
async def test_transit_finished_to_turns(
    lobby: Lobby, egor: Player, anton: Player
) -> None:
    assert lobby.game  # TODO: Do something with it
    lobby.transit_to(Finished(anton, lobby.game.setups.get_card()))
    punchline_card = lobby.game.punchlines.get_card()
    lobby.table.append(CardOnTable(punchline_card, anton))
    next_setup_card = lobby.game.setups.cards[-1]

    egor.continue_game()

    assert isinstance(lobby.state, Turns)
    assert lobby.lead is anton
    assert lobby.state.setup == next_setup_card
