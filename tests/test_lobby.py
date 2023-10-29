import pytest

from lobby import Lobby, Player, SetupCard, PunchlineCard, PlayerNotPunchlineCardHolderError, CardOnTable, \
    PlayerNotDealerError, Deck


@pytest.fixture
def setup_card() -> SetupCard:
    return SetupCard()


@pytest.fixture
def punchline_card() -> PunchlineCard:
    return PunchlineCard()


@pytest.fixture
def deck(setup_card: SetupCard, punchline_card: PunchlineCard) -> Deck:
    return Deck(setup_cards=[setup_card], punchline_cards=[punchline_card])

@pytest.fixture
def player_1(lobby: Lobby) -> Player:
    player = Player(punchline_cards=[])
    lobby.players.append(player)
    return player

@pytest.fixture
def lobby() -> Lobby:
    lobby = Lobby(
        players=[player_1, player_2],
        lead=player_3,
        owner=player_1,
        setup_card=SetupCard()
    )


@pytest.fixture
def player_1(lobby: Lobby) -> Player:
    player = Player(punchline_cards=[])
    lobby.players.append(player)
    return player

@pytest.fixture
def player_2(lobby: Lobby) -> Player:
    player = Player(punchline_cards=[])
    lobby.players.append(player)
    return player


@pytest.fixture
def player_3(lobby: Lobby) -> Player:
    player = Player(punchline_cards=[])
    lobby.players.append(player)
    return player


def test_in_memory_deck_get_random_setup_card(
    deck: Deck, setup_card: SetupCard
) -> None:
    assert deck.get_random_setup_card() is setup_card


def test_in_memory_deck_get_random_punchline_card(
    deck: Deck, punchline_card: PunchlineCard
) -> None:
    assert deck.get_random_punchline_card() is punchline_card


def test_lobby_change_lead() -> None:
    player_1 = Player(punchline_cards=[])
    player_2 = Player(punchline_cards=[])
    player_3 = Player(punchline_cards=[])
    lobby = Lobby(
        players=[player_1, player_2],
        lead=player_3,
        owner=player_1,
        setup_card=SetupCard()
    )
    lobby.change_lead()
    assert lobby.players == [player_2, player_3]
    assert lobby.lead is player_1


def test_lobby_change_setup_card() -> None:
    player_1 = Player(punchline_cards=[])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_1,
        players=[],
        owner=player_1,
        setup_card=setup_card
    )
    new_setup_card = SetupCard()
    lobby.change_setup_card(new_setup_card)
    assert lobby.setup_card is new_setup_card


def test_lobby_choose_punchline_card() -> None:
    punchline_card = PunchlineCard()
    player_1 = Player(punchline_cards=[punchline_card])
    player_2 = Player(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_2,
        players=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    lobby.choose_punchline_card(player_1, punchline_card)
    assert punchline_card is lobby.get_card_from_table(punchline_card).card
    assert punchline_card not in player_1.punchline_cards


def test_lobby_choose_punchline_member_not_punchline_holder() -> None:
    punchline_card = PunchlineCard()
    player_1 = Player(punchline_cards=[punchline_card])
    player_2 = Player(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_2,
        players=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    with pytest.raises(PlayerNotPunchlineCardHolderError):
        lobby.choose_punchline_card(player_2, punchline_card)


def test_open_punchline_card() -> None:
    punchline_card = PunchlineCard()
    player_1 = Player(punchline_cards=[punchline_card])
    player_2 = Player(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_2,
        players=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    lobby.choose_punchline_card(player_1, punchline_card)
    lobby.open_punchline_card(player_2, punchline_card)
    assert isinstance(lobby.table[0], CardOnTable)


def test_open_punchline_card_member_not_lead() -> None:
    punchline_card = PunchlineCard()
    player_1 = Player(punchline_cards=[punchline_card])
    player_2 = Player(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_2,
        players=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    with pytest.raises(PlayerNotDealerError):
        lobby.open_punchline_card(player_1, punchline_card)


def test_lobby_lead_choose_punchline_card() -> None:
    punchline_card = PunchlineCard()
    player_1 = Player(punchline_cards=[punchline_card])
    player_2 = Player(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        lead=player_2,
        players=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    lobby.choose_punchline_card(player_1, punchline_card)
    lobby.open_punchline_card(player_2, punchline_card)
    lobby.lead_choose_punchline_card(punchline_card)
    assert player_1.score == 1

