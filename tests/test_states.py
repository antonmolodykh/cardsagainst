from lobby import Deck, Judgement, Lobby, Player, PunchlineCard, Turns


def test_transit_gathering_to_turns(lobby: Lobby) -> None:
    lobby.state.start_turn()
    isinstance(lobby.state, Turns)


def test_transit_turns_to_judgement(
    lobby: Lobby, anton: Player, punchline_deck: Deck[PunchlineCard]
) -> None:
    lobby.add_player(anton)
    punchline_card = punchline_deck.get_card()
    anton.add_punchline_card(punchline_card)
    lobby.transit_to(Turns())
    lobby.state.choose_punchline_card(anton, punchline_card)
    assert isinstance(lobby.state, Judgement)
