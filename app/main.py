"""Main app which serves the application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from mangum import Mangum

from app.api.config.database import create_table
from app.api.config.settings import get_setting
from app.api.routers.nemo import nemo_route


settings = get_setting()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Connect to database on startup."""
    await create_table()
    # await database.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     """Disconnect to database on shutdown."""
#     await database.disconnect()


@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return HTMLResponse(content="<h1> Welcome to Nemo 🥳</h1> ", status_code=200)


app.include_router(
    nemo_route,
    prefix="/nemo",
    tags=["Nemo"],
)

handler = Mangum(app)
