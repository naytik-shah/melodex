from datetime import datetime

from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("albums.id", ondelete="CASCADE"), nullable=True, index=True
    )
    song_id: Mapped[int | None] = mapped_column(
        ForeignKey("songs.id", ondelete="CASCADE"), nullable=True, index=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Python-level only -- no columns added, so no migration needed. Lets a
    # profile show *what* was rated, not just an id.
    album: Mapped[Optional["Album"]] = relationship(lazy="joined")
    song: Mapped[Optional["Song"]] = relationship(lazy="joined")

    __table_args__ = (
        # Exactly one of album_id / song_id is set (TRD 7.4)
        CheckConstraint(
            "(album_id IS NOT NULL AND song_id IS NULL) OR (album_id IS NULL AND song_id IS NOT NULL)",
            name="ck_ratings_exactly_one_target",
        ),
        CheckConstraint("value >= 1 AND value <= 10", name="ck_ratings_value_range"),
        # One rating per user per item, enforced at the database level (TRD 7.4)
        UniqueConstraint("user_id", "album_id", name="uq_ratings_user_album"),
        UniqueConstraint("user_id", "song_id", name="uq_ratings_user_song"),
    )
