from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""


metadata = Base.metadata


class Punchline(Base):
    __tablename__ = "punchlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[list[tuple[str, list[str]]]] = mapped_column(JSONB, nullable=False)
