from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.rating import Rating


def get_rating_stats(
    db: Session,
    *,
    album_id: int | None = None,
    song_id: int | None = None,
) -> tuple[float | None, int]:
    """Average rating and rating count for a single album or song.

    Returns (None, 0) when nothing has been rated yet -- never (0, 0).
    This is the one shared place that rule lives, instead of being
    reimplemented on albums, songs and ratings separately (TRD cross-feature notes).
    """
    query = db.query(func.avg(Rating.value), func.count(Rating.id))

    if album_id is not None:
        query = query.filter(Rating.album_id == album_id)
    else:
        query = query.filter(Rating.song_id == song_id)

    average, count = query.one()
    return (round(float(average), 2) if average is not None else None, count)
