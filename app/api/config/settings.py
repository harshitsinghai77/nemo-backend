import os
from functools import lru_cache
from typing import List

class Settings:
    APP_NAME = "Nemo"
    SQLITE_DB_NAME = "sqlite_db_prod.db" if os.getenv("ENV") == "prod" else "sqlite_db_dev.db"
    SQLITE_CLOUD_DB = "nemo-prod.sqlite"
    SQLITE_LOCAL_PATH = f"/tmp/{SQLITE_DB_NAME}" if os.getenv("ENV") == "prod" else SQLITE_DB_NAME
    SQLITE_S3_BUCKET = "nemo-app-db"
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
    
    class Config:
        case_sensitive: bool = True


@lru_cache
def get_setting():
    return Settings()
