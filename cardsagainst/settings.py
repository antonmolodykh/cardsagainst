from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class LobbySettings:
    turn_duration: int | None = None
    winning_score: int
    finish_delay: int = 5
    start_turn_delay: int = 5
