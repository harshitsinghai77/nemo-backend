"""Main app which serves the application."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nemo.config.database import database, engine, metadata
from nemo.config.settings import get_setting
from nemo.routers.nemo import nemo_route
from nemo.routers.spotify import spotify_auth

settings = get_setting()
metadata.create_all(engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Connect to database on startup."""
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect to database on shutdown."""
    await database.disconnect()


@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return "App succesfully running."


app.include_router(
    spotify_auth,
    prefix="/authorize-spotify",
    tags=["SpotifyAuth"],
)

app.include_router(
    nemo_route,
    prefix="/nemo",
    tags=["Nemo"],
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
