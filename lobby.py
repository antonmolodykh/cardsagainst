from typing import Collection
from queue import Queue
from uuid import uuid4

from pydantic import BaseModel, Field
from typing_extensions import Annotated

lobbies = {}


class MemberNotPunchlineCardHolderError(Exception):
    pass


class MemberNotDealerError(Exception):
    pass


# class State(Enum):
#     MOVE = "move"
#     JUDGING = "judging"
#     PENDING_START = "pending start"
#     FINISHED = "finished"

class SetupCard(BaseModel):
    uid: Annotated[uuid4, Field(default_factory=uuid4)]


class PunchlineCard(BaseModel):
    uid: Annotated[uuid4, Field(default_factory=uuid4)]


class Member(BaseModel):
    uid: Annotated[uuid4, Field(default_factory=uuid4)]
    punchline_cards: list[PunchlineCard]


class OpenedPunchlineCard(BaseModel):
    card: PunchlineCard


class Lobby:
    uid: uuid4
    members: list[Member]
    dealer: Member
    owner: Member
    setup_card: SetupCard
    punchline_cards: list[PunchlineCard | OpenedPunchlineCard]

    def __init__(
        self,
        members: Collection[Member],
        dealer: Member,
        owner: Member,
        setup_card: SetupCard,
    ) -> None:
        self.members = list(members)
        self.dealer = dealer
        self.owner = owner
        self.setup_card = setup_card
        self.punchline_cards = []
        self.uid = uuid4()

    def change_dealer(self) -> None:
        self.members.append(self.dealer)
        self.dealer = self.members.pop(0)

    def change_setup_card(self, card: SetupCard) -> None:
        self.setup_card = card

    def choose_punchline_card(self, member: Member, card: PunchlineCard) -> None:
        if card not in member.punchline_cards:
            raise MemberNotPunchlineCardHolderError
        self.punchline_cards.append(card)
        member.punchline_cards.remove(card)

    def open_punchline_card(self, member: Member, card: PunchlineCard) -> None:
        if self.dealer is not member:
            raise MemberNotDealerError

        index = self.punchline_cards.index(card)
        self.punchline_cards[index] = OpenedPunchlineCard(card=card)

    # def __init__(self, owner: int):
    #     self.uid = uuid4()
    #     self.owner = owner
    #     self.members = [self.owner]

    # def add_member(self, member: int):
    #     self.members.append(member)

