from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RatingCreate(BaseModel):
    value: int


class RatingRead(BaseModel):
    id: int
    value: int
    album_id: int | None
    song_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingResponse(BaseModel):
    rating: RatingRead
    average_rating: float | None
    rating_count: int
