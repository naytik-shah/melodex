from typing import Literal

from pydantic import BaseModel


class SearchArtistResult(BaseModel):
    type: Literal["artist"] = "artist"
    id: int
    name: str
    image_url: str | None


class SearchAlbumResult(BaseModel):
    type: Literal["album"] = "album"
    id: int
    title: str
    cover_url: str | None
    artist_name: str


class SearchSongResult(BaseModel):
    type: Literal["song"] = "song"
    id: int
    title: str
    album_title: str
    artist_name: str


class SearchResults(BaseModel):
    """Grouped by type rather than one mixed ranked list (TRD 6.8)."""

    artists: list[SearchArtistResult]
    albums: list[SearchAlbumResult]
    songs: list[SearchSongResult]
