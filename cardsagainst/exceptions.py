from __future__ import annotations


class CardNotInPlayerHandError(Exception):
    pass


class PlayerNotLeadError(Exception):
    pass


class PlayerNotOwnerError(Exception):
    pass


class NotAllCardsOpenedError(Exception):
    pass


class UnknownPlayerError(Exception):
    pass


class PlayerAlreadyReadyError(Exception):
    pass


class ScoreTooLowError(Exception):
    pass
