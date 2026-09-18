from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class RatedItem(BaseModel):
    """The album or song a rating points at -- enough to render and link it."""

    type: Literal["album", "song"]
    id: int
    title: str


class ProfileRating(BaseModel):
    value: int
    created_at: datetime
    updated_at: datetime
    item: RatedItem


class PublicProfile(BaseModel):
    """What anyone -- guest or logged in -- may see. Deliberately no email."""

    username: str
    created_at: datetime
    ratings: list[ProfileRating]


class PrivateProfile(PublicProfile):
    """The owner's own view: the public profile plus their email (TRD 2.5)."""

    id: int
    email: str
