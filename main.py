import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from noiist.config.database import database, engine, metadata
from noiist.config.settings import get_setting
from noiist.routers.spotify import spotify_auth

from fastapi.templating import Jinja2Templates


settings = get_setting()
metadata.create_all(engine)

app = FastAPI(title=settings.APP_NAME)
app.mount(
    "/static",
    StaticFiles(directory="frontend/build/static"),
    name="static",
)
templates = Jinja2Templates(directory="frontend/build")

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


@app.get("/")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/authorization-success")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/get-started")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(
    spotify_auth,
    prefix="/authorize-spotify",
    tags=["SpotifyAuth"],
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)