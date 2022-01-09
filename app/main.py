"""Main app which serves the application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from api.config.database import create_table, close_connection
from api.config.settings import get_setting
from api.routers.nemo import nemo_route
from api.routers.livepeer import livepeer_route


settings = get_setting()
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
    await create_table()


@app.on_event("shutdown")
async def shutdown():
    """Disconnect to database on shutdown."""
    await close_connection()


@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return HTMLResponse(content="<h1> Welcome to Nemo 🥳</h1> ", status_code=200)


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

# Only for AWS Lambda Deployment
# handler = Mangum(app)
