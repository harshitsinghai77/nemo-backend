"""Main app which serves the application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from mangum import Mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import HTMLResponse
from sqlmodel import SQLModel

import app.api.models.nemo
from app.api.config.database_sqlite import engine

from app.api.config.settings import get_setting
from app.api.routers.nemo import nemo_route

settings = get_setting()

# Function to handle both startup and shutdown using lifespan
@asynccontextmanager
async def lifespan_context(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup logic
    print("Starting app...")
    print("Initializing database tables")
    SQLModel.metadata.create_all(engine)  # Create tables during startup

    yield  # FastAPI runs the app here

    # Perform shutdown tasks (e.g., closing DB connections)
    # Shutdown logic
    print("Shutting down...")
    engine.dispose()  # Close all connections

app = FastAPI(lifespan=lifespan_context, title=settings.APP_NAME)

app.add_middleware(HTTPSRedirectMiddleware)  # Force HTTPS for security
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    """Generic message if backend is deployed succesfully."""
    return HTMLResponse(content="<h1> Welcome to Nemo.🥳</h1> ", status_code=200)

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(
    nemo_route,
    prefix="/nemo",
    tags=["Nemo"],
)

# Add Mangum handler for AWS Lambda
handler = Mangum(app)
