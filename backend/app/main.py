from fastapi import FastAPI
from app.routers import albums, artists, auth, ratings, search, songs, users

app = FastAPI(title="Melodex")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(artists.router)
app.include_router(albums.router)
app.include_router(songs.router)
app.include_router(ratings.router)
app.include_router(search.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}