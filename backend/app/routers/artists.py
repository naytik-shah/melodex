from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.artist import Artist
from app.schema.artist import ArtistRead
from app.schema.summary import ArtistSummary

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("", response_model=list[ArtistSummary])
def list_artists(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Artist).order_by(Artist.name).limit(limit).offset(offset).all()


@router.get("/{artist_id}", response_model=ArtistRead)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    artist = db.get(Artist, artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")

    # An artist with no albums returns an empty list, not an error (TRD 3.6)
    return artist
