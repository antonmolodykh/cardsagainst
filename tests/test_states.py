from lobby import Lobby, Turns


def test_transit_gathering_to_turns(lobby: Lobby) -> None:
    lobby.state.start_turn()
    isinstance(lobby.state, Turns)
