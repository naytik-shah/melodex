from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.genre import Genre, album_genres


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    release_date: Mapped[date] = mapped_column(Date, nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    artist: Mapped["Artist"] = relationship(back_populates="albums", lazy="joined")
    genres: Mapped[list[Genre]] = relationship(secondary=album_genres, lazy="selectin")
    songs: Mapped[list["Song"]] = relationship(
        back_populates="album",
        lazy="selectin",
        order_by="Song.track_number",
    )
