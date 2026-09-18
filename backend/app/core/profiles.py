from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.models.user import User
from app.schema.profile import ProfileRating, RatedItem


def get_user_ratings(
    db: Session,
    user: User,
    *,
    limit: int,
    offset: int,
) -> list[ProfileRating]:
    """A user's ratings, newest first, paginated (TRD 2.6).

    Shared by the public profile and the owner's own /auth/me view so the
    two can never drift apart.
    """
    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user.id)
        .order_by(Rating.updated_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    results: list[ProfileRating] = []
    for rating in ratings:
        if rating.album is not None:
            item = RatedItem(type="album", id=rating.album.id, title=rating.album.title)
        else:
            item = RatedItem(type="song", id=rating.song.id, title=rating.song.title)

        results.append(
            ProfileRating(
                value=rating.value,
                created_at=rating.created_at,
                updated_at=rating.updated_at,
                item=item,
            )
        )

    return results
