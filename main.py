import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from noiist.config.database import database, engine, metadata
from noiist.config.settings import get_setting
from noiist.routers.noisli import noisli_route
from noiist.routers.spotify import spotify_auth

settings = get_setting()
metadata.create_all(engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def index():
    return "App succesfully running."


app.include_router(
    spotify_auth,
    prefix="/authorize-spotify",
    tags=["SpotifyAuth"],
)

app.include_router(
    noisli_route,
    prefix="/noisli",
    tags=["Noisli"],
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
