from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schema.genre import GenreRead
from app.schema.summary import AlbumSummary


class ArtistRead(BaseModel):
    id: int
    name: str
    bio: str | None
    image_url: str | None
    created_at: datetime
    genres: list[GenreRead]
    albums: list[AlbumSummary]

    model_config = ConfigDict(from_attributes=True)
