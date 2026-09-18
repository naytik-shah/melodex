from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.ratings import get_rating_stats
from app.db.session import get_db
from app.models.song import Song
from app.schema.song import SongRead
from app.schema.summary import AlbumSummary, ArtistSummary

router = APIRouter(prefix="/songs", tags=["songs"])


@router.get("/{song_id}", response_model=SongRead)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")

    average_rating, rating_count = get_rating_stats(db, song_id=song.id)

    return SongRead(
        id=song.id,
        title=song.title,
        track_number=song.track_number,
        duration_seconds=song.duration_seconds,
        created_at=song.created_at,
        album=AlbumSummary.model_validate(song.album),
        # Artist is reached through the album, never stored on the song
        artist=ArtistSummary.model_validate(song.album.artist),
        average_rating=average_rating,
        rating_count=rating_count,
    )
