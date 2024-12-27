import os

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from app.api.config.settings import get_setting

settings = get_setting()
sqlite_file_name = settings.SQLITE_LOCAL_PATH
if os.getenv("ENV") == "running_tests":
    sqlite_file_name = os.getenv("TEST_SQLITE_FILE_NAME")

sqlite_url = f"sqlite:///{sqlite_file_name}"

# Enable foreign key constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

engine = create_engine(sqlite_url)
