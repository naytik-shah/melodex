from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schema.genre import GenreRead
from app.schema.summary import ArtistSummary


class TrackRead(BaseModel):
    id: int
    title: str
    track_number: int
    duration_seconds: int

    model_config = ConfigDict(from_attributes=True)


class AlbumListItem(BaseModel):
    id: int
    title: str
    release_date: date
    cover_url: str | None
    artist: ArtistSummary

    model_config = ConfigDict(from_attributes=True)


class AlbumRead(BaseModel):
    id: int
    title: str
    release_date: date
    cover_url: str | None
    created_at: datetime
    artist: ArtistSummary
    genres: list[GenreRead]
    tracklist: list[TrackRead]
    average_rating: float | None
    rating_count: int
