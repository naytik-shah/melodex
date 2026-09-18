from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.song import Song
from app.schema.search import (
    SearchAlbumResult,
    SearchArtistResult,
    SearchResults,
    SearchSongResult,
)

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResults)
def search(
    q: str = Query(default=""),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    # Trimmed and lowercased server-side before matching (TRD 6.6)
    query = q.strip().lower()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")

    contains = f"%{query}%"
    starts_with = f"{query}%"

    # Exact prefix matches rank above plain contains-matches (TRD 6.3).
    # ilike is case-insensitive, so "beatles" finds "The Beatles".
    artists = (
        db.query(Artist)
        .filter(Artist.name.ilike(contains))
        .order_by(case((Artist.name.ilike(starts_with), 0), else_=1), Artist.name)
        .limit(limit)
        .all()
    )

    albums = (
        db.query(Album)
        .filter(Album.title.ilike(contains))
        .order_by(case((Album.title.ilike(starts_with), 0), else_=1), Album.title)
        .limit(limit)
        .all()
    )

    songs = (
        db.query(Song)
        .filter(Song.title.ilike(contains))
        .order_by(case((Song.title.ilike(starts_with), 0), else_=1), Song.title)
        .limit(limit)
        .all()
    )

    # No matches returns empty arrays with a 200, never an error (TRD 6.6)
    return SearchResults(
        artists=[
            SearchArtistResult(id=a.id, name=a.name, image_url=a.image_url) for a in artists
        ],
        albums=[
            SearchAlbumResult(
                id=a.id, title=a.title, cover_url=a.cover_url, artist_name=a.artist.name
            )
            for a in albums
        ],
        songs=[
            SearchSongResult(
                id=s.id,
                title=s.title,
                album_title=s.album.title,
                artist_name=s.album.artist.name,
            )
            for s in songs
        ],
    )
