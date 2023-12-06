import asyncio

from lobby import Deck, Judgement, Lobby, Player, PunchlineCard, SetupCard, Turns


def test_transit_gathering_to_turns(lobby: Lobby) -> None:
    lobby.state.start_turn()
    isinstance(lobby.state, Turns)


def test_transit_turns_to_judgement(
    lobby: Lobby,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    setup_deck: Deck[SetupCard],
) -> None:
    setup_card = setup_deck.get_card()
    lobby.add_player(anton)
    punchline_card = punchline_deck.get_card()
    anton.add_punchline_card(punchline_card)
    lobby.transit_to(Turns(setup_card))
    lobby.state.choose_punchline_card(anton, punchline_card)
    assert isinstance(lobby.state, Judgement)
    assert lobby.state.setup is setup_card


def test_transit_judgement_to_turns(
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


async def test_transit_judgement_to_finished(
    lobby: Lobby,
    anton: Player,
    punchline_deck: Deck[PunchlineCard],
    setup_deck: Deck[SetupCard],
) -> None:
    setup_card = setup_deck.get_card()
    lobby.add_player(anton)
    lobby.transit_to(Judgement(setup_card))
    lobby.state.start_turn()
    punchline_card = anton.hand[0]
    lobby.state.choose_punchline_card(anton, punchline_card)
    lobby.state.pick_turn_winner(punchline_card)
    await asyncio.sleep(0.01)
    assert isinstance(lobby.state, Finished)
