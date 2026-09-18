from datetime import date

from pydantic import BaseModel, ConfigDict

# Small "reference" shapes used wherever one entity is nested inside another
# (an album listed on an artist page, the artist shown on a song page).
# They live in their own module so artist.py and album.py can both use them
# without importing each other in a circle.


class ArtistSummary(BaseModel):
    id: int
    name: str
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class AlbumSummary(BaseModel):
    id: int
    title: str
    release_date: date
    cover_url: str | None

    model_config = ConfigDict(from_attributes=True)
