import os

# from urllib.parse import quote

import databases
import sqlalchemy

DB_NAME = os.getenv("DB_NAME", "nemo")
DB_USER = os.getenv("DB_USER", "nemo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_MAX_SIZE = 10

environment = os.getenv("ENV", "development")

# ENCODED_PASSWORD = quote(DB_PASSWORD)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
if environment == "development":
    DATABASE_URL = "postgresql://nemo:password@localhost:5432/nemo"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
