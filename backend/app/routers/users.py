from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.profiles import get_user_ratings
from app.db.session import get_db
from app.models.user import User
from app.schema.profile import PublicProfile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=PublicProfile)
def get_public_profile(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # PublicProfile has no email field, so it cannot be exposed here (TRD 2.2).
    # A user with zero ratings returns an empty list, not an error (TRD 2.10).
    return PublicProfile(
        username=user.username,
        created_at=user.created_at,
        ratings=get_user_ratings(db, user, limit=limit, offset=offset),
    )
