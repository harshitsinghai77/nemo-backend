import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME = "Noiist"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 Days
    JWT_TOKEN_TYPE: str = "bearer"

    REGISTRATION_TOKEN_LIFETIME = 60 * 60
    TOKEN_ALGORITHM = "HS256"
    API_PREFIX = "/api"
    HOST = "localhost"
    PORT = 3000
    BASE_URL = "{}:{}/".format(HOST, str(PORT))
    MODELS = [
        "noiist.models.users",
    ]

    class Config:
        case_sensitive: bool = True


@lru_cache
def get_setting():
    return Settings()
