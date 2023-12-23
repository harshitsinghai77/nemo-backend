import os
from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME = "Nemo"
    USE_POSTGRES_DATABASE = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 Days
    JWT_TOKEN_TYPE: str = "bearer"
    BACKEND_CORS_ORIGINS: List[str] = ["https://nemo-app.netlify.app"]
    if os.getenv("ENV") == "development":
        BACKEND_CORS_ORIGINS.append("http://localhost:3000")

    REGISTRATION_TOKEN_LIFETIME = 60 * 60
    TOKEN_ALGORITHM = "HS256"
    API_PREFIX = "/api"
    HOST = "localhost"
    PORT = 3000
    BASE_URL = "{}:{}/".format(HOST, str(PORT))
    MODELS = [
        "nemo.models.users",
    ]

    class Config:
        case_sensitive: bool = True


@lru_cache
def get_setting():
    return Settings()
