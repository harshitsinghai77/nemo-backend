import os

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from app.api.config.settings import get_setting

settings = get_setting()

SQLITE_CLOUD_API_KEY = os.getenv("SQLITE_CLOUD_API_KEY")
SQLITE_CLOUD_HOST = os.getenv("SQLITE_CLOUD_HOST")

sqlite_url = f"sqlitecloud://{SQLITE_CLOUD_HOST}:8860/{settings.SQLITE_CLOUD_DB}?apikey={SQLITE_CLOUD_API_KEY}"

if os.getenv("ENV") == "running_tests":
    # Local SQLite DB for running pytests 
    sqlite_file_name = os.getenv("TEST_SQLITE_FILE_NAME")
    sqlite_url = f"sqlite:///{sqlite_file_name}"

# Enable foreign key constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

engine = create_engine(sqlite_url)
