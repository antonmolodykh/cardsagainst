from unittest.mock import Mock, call

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
    SetupCard,
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
    assert setup_cards_deck.get_random_card() is setup_card


@pytest.fixture
def observer() -> LobbyObserver:
    return Mock(LobbyObserver)


@pytest.fixture
def egor(observer: LobbyObserver) -> Player:
    return Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=observer,
    )


@pytest.fixture
def anton(observer: LobbyObserver) -> Player:
    return Player(
        profile=Profile(name="anton", emoji="🍎", background_color="#ff0000"),
        observer=observer,
    )


@pytest.fixture
def yura(observer: LobbyObserver) -> Player:
    return Player(
        profile=Profile(name="yura", emoji="🍎", background_color="#ff0000"),
        observer=observer,
    )


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
    punchline_card = punchline_cards_deck.get_random_card()
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
    punchline_card = punchline_cards_deck.get_random_card()
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
    punchline_card = punchline_cards_deck.get_random_card()
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
    punchline_card = punchline_cards_deck.get_random_card()
    egor.punchline_cards.append(punchline_card)
    lobby.choose_punchline_card(egor, punchline_card)
    lobby.open_punchline_card(anton, punchline_card)
    lobby.lead_choose_punchline_card(punchline_card)
    assert egor.score == 1


def test_player_joined(
    egor: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    yura_mock = Mock()
    yura = Player(
        profile=Profile(name="egor", emoji="🍎", background_color="#ff0000"),
        observer=yura_mock,
    )

    observer.attach_mock(yura_mock, "yura")
    # observer.attach_mock(egor_mock, "egor")

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
        call.yura.player_joined(yura),
        # call.egor.player_joined(),
    ]
    observer.assert_has_calls(expected_events)


def test_player_connected(
    egor: Player,
    yura: Player,
    setup_cards_deck: Deck[SetupCard],
    punchline_cards_deck: Deck[PunchlineCard],
    observer: Mock,
) -> None:
    # FIXME: Lobby is not used. Looks like lobby must be required to send events
    # lobby = Lobby(
    #     lead=egor,
    #     players=[yura],
    #     owner=egor,
    #     setups=setup_cards_deck,
    #     punchlines=punchline_cards_deck,
    #     observer=observer,
    # )
    # FIXME: I want to test which player has received the message
    yura.set_connected()
    expected_events = [
        call.player_connected(yura),
    ]
    observer.assert_has_calls(expected_events)
