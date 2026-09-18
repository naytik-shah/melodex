from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.ratings import get_rating_stats
from app.db.session import get_db
from app.models.album import Album
from app.models.rating import Rating
from app.models.song import Song
from app.models.user import User
from app.routers.auth import get_current_user
from app.schema.rating import RatingCreate, RatingRead, RatingResponse

router = APIRouter(tags=["ratings"])


def _upsert_rating(
    db: Session,
    user: User,
    payload: RatingCreate,
    *,
    album_id: int | None = None,
    song_id: int | None = None,
) -> RatingResponse:
    if payload.value < 1 or payload.value > 10:
        raise HTTPException(status_code=400, detail="Rating value must be between 1 and 10")

    query = db.query(Rating).filter(Rating.user_id == user.id)
    if album_id is not None:
        query = query.filter(Rating.album_id == album_id)
    else:
        query = query.filter(Rating.song_id == song_id)

    rating = query.first()
    if rating is None:
        # First time this user rates this item
        rating = Rating(user_id=user.id, album_id=album_id, song_id=song_id, value=payload.value)
        db.add(rating)
    else:
        # Already rated -> update in place, never create a duplicate (TRD 7.6)
        rating.value = payload.value

    db.commit()
    db.refresh(rating)

    average_rating, rating_count = get_rating_stats(db, album_id=album_id, song_id=song_id)

    return RatingResponse(
        rating=RatingRead.model_validate(rating),
        average_rating=average_rating,
        rating_count=rating_count,
    )


@router.post("/albums/{album_id}/ratings", response_model=RatingResponse)
def rate_album(
    album_id: int,
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.get(Album, album_id) is None:
        raise HTTPException(status_code=404, detail="Album not found")

    return _upsert_rating(db, current_user, payload, album_id=album_id)


@router.post("/songs/{song_id}/ratings", response_model=RatingResponse)
def rate_song(
    song_id: int,
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if db.get(Song, song_id) is None:
        raise HTTPException(status_code=404, detail="Song not found")

    return _upsert_rating(db, current_user, payload, song_id=song_id)


@router.get("/albums/{album_id}/ratings/me", response_model=RatingRead)
def get_my_album_rating(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rating = (
        db.query(Rating)
        .filter(Rating.user_id == current_user.id, Rating.album_id == album_id)
        .first()
    )
    if rating is None:
        raise HTTPException(status_code=404, detail="You have not rated this album")

    return rating
