from __future__ import annotations

from pydantic import BaseModel


class Profile(BaseModel):
    name: str
    emoji: str
