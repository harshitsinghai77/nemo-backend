"""Main app which serves the application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.config.database import close_connection, create_table
from app.api.config.settings import get_setting
from app.api.routers.livepeer import livepeer_route
from app.api.routers.nemo import nemo_route
from app.api.routers.nemo_deta import nemo_deta_route

settings = get_setting()
use_database = settings.USE_DATABSE
detabase = True if use_database == "DETA" else False
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Connect to database on startup."""
    if not detabase:
        await create_table()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect to database on shutdown."""
    if not detabase:
        await close_connection()


@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return HTMLResponse(content="<h1> Welcome to Nemo 🥳</h1> ", status_code=200)


nemo_route = nemo_deta_route if detabase else nemo_route
app.include_router(
    nemo_route,
    prefix="/nemo",
    tags=["Nemo"],
)

app.include_router(
    livepeer_route,
    prefix="/stream",
    tags=["Livepeer"],
)
