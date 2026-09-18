# Importing every model here guarantees they are all registered on
# Base.metadata before SQLAlchemy configures mappers or Alembic autogenerates.
from app.models.album import Album
from app.models.artist import Artist
from app.models.genre import Genre, album_genres, artist_genres
from app.models.rating import Rating
from app.models.song import Song
from app.models.user import User

__all__ = [
    "Album",
    "Artist",
    "Genre",
    "Rating",
    "Song",
    "User",
    "album_genres",
    "artist_genres",
]
