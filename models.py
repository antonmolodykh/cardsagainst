import datetime
from enum import IntEnum

from sqlalchemy import Text, Boolean, Date, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""


metadata = Base.metadata


class Punchline(Base):
    __tablename__ = "punchlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    variants: Mapped[list[tuple[str, list[str]]]] = mapped_column(JSONB, nullable=False)


class Setup(Base):
    __tablename__ = "setups"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant: Mapped[str] = mapped_column(Text, nullable=False)
    starts_with_punchline: Mapped[bool] = mapped_column(Boolean, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class Changelog(Base):
    __tablename__ = "changelog"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class GameStats(Base):
    __tablename__ = "game_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    winning_score: Mapped[int] = mapped_column(nullable=False)
    turn_duration: Mapped[int] = mapped_column(nullable=False)
    hand_size: Mapped[int] = mapped_column(nullable=False)


class CardEventType(IntEnum):
    moved_to_hand = 0
    moved_to_table = 1
    won = 2
    dumped = 3
    flushed = 4


class StatsCardsEvents(Base):
    __tablename__ = "stats_cards_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    punchline_id: Mapped[int] = mapped_column(ForeignKey("punchlines.id"), nullable=False)
    event_type_id: Mapped[CardEventType] = mapped_column(nullable=False)
    setup_id: Mapped[int] = mapped_column(ForeignKey("setups.id"), nullable=False)
