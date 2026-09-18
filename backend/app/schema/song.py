from datetime import datetime

from pydantic import BaseModel

from app.schema.summary import AlbumSummary, ArtistSummary


class SongRead(BaseModel):
    id: int
    title: str
    track_number: int
    duration_seconds: int
    created_at: datetime
    album: AlbumSummary
    artist: ArtistSummary
    average_rating: float | None
    rating_count: int
