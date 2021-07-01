import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from noiist.config.database import database, engine, metadata
from noiist.config.settings import get_setting
from noiist.routers.spotify import spotify_auth
from noiist.routers.noisli import noisli_route

settings = get_setting()
metadata.create_all(engine)

app = FastAPI(title=settings.APP_NAME)
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

<<<<<<< HEAD
@app.get('/')
def index():
    return "App succesfully running."
=======

@app.get("/")
async def serve_landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/authorization-success")
async def serve_athorization(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/get-started")
async def serve_get_started(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

>>>>>>> 9ccaa83 (Add new dependency)

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
