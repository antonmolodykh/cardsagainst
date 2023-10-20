import pytest

from lobby import Lobby, Member, SetupCard, PunchlineCard, MemberNotPunchlineCardHolderError, OpenedPunchlineCard, \
    MemberNotDealerError


def test_lobby_change_dealer() -> None:
    player_1 = Member(punchline_cards=[])
    player_2 = Member(punchline_cards=[])
    player_3 = Member(punchline_cards=[])
    lobby = Lobby(
        members=[player_1, player_2],
        dealer=player_3,
        owner=player_1,
        setup_card=SetupCard()
    )
    lobby.change_dealer()
    assert lobby.members == [player_2, player_3]
    assert lobby.dealer is player_1


def test_lobby_change_setup_card() -> None:
    player_1 = Member(punchline_cards=[])
    setup_card = SetupCard()
    lobby = Lobby(
        dealer=player_1,
        members=[],
        owner=player_1,
        setup_card=setup_card
    )
    new_setup_card = SetupCard()
    lobby.change_setup_card(new_setup_card)
    assert lobby.setup_card is new_setup_card


def test_lobby_choose_punchline_card() -> None:
    punchline_card = PunchlineCard()
    player_1 = Member(punchline_cards=[punchline_card])
    player_2 = Member(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        dealer=player_2,
        members=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    lobby.choose_punchline_card(player_1, punchline_card)
    assert punchline_card in lobby.punchline_cards
    assert punchline_card not in player_1.punchline_cards


def test_lobby_choose_punchline_member_not_punchline_holder() -> None:
    punchline_card = PunchlineCard()
    player_1 = Member(punchline_cards=[punchline_card])
    player_2 = Member(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        dealer=player_2,
        members=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    with pytest.raises(MemberNotPunchlineCardHolderError):
        lobby.choose_punchline_card(player_2, punchline_card)


def test_open_punchline_card() -> None:
    punchline_card = PunchlineCard()
    player_1 = Member(punchline_cards=[punchline_card])
    player_2 = Member(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        dealer=player_2,
        members=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    lobby.choose_punchline_card(player_1, punchline_card)
    lobby.open_punchline_card(player_2, punchline_card)
    assert isinstance(lobby.punchline_cards[0], OpenedPunchlineCard)


def test_open_punchline_card_member_not_dealer() -> None:
    punchline_card = PunchlineCard()
    player_1 = Member(punchline_cards=[punchline_card])
    player_2 = Member(punchline_cards=[PunchlineCard()])
    setup_card = SetupCard()
    lobby = Lobby(
        dealer=player_2,
        members=[player_1],
        owner=player_1,
        setup_card=setup_card
    )
    with pytest.raises(MemberNotDealerError):
        lobby.open_punchline_card(player_1, punchline_card)
