from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.ratings import get_rating_stats
from app.db.session import get_db
from app.models.album import Album
from app.schema.album import AlbumListItem, AlbumRead, TrackRead
from app.schema.genre import GenreRead
from app.schema.summary import ArtistSummary

router = APIRouter(prefix="/albums", tags=["albums"])


@router.get("", response_model=list[AlbumListItem])
def list_albums(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Album).order_by(Album.title).limit(limit).offset(offset).all()


@router.get("/{album_id}", response_model=AlbumRead)
def get_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(Album, album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")

    average_rating, rating_count = get_rating_stats(db, album_id=album.id)

    return AlbumRead(
        id=album.id,
        title=album.title,
        release_date=album.release_date,
        cover_url=album.cover_url,
        created_at=album.created_at,
        artist=ArtistSummary.model_validate(album.artist),
        genres=[GenreRead.model_validate(genre) for genre in album.genres],
        # album.songs is ordered by track_number by the relationship (TRD 4.6)
        tracklist=[TrackRead.model_validate(song) for song in album.songs],
        average_rating=average_rating,
        rating_count=rating_count,
    )
