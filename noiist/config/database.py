import os

import databases
import sqlalchemy

DB_NAME = os.getenv("DB_NAME", "habitt")
DB_USER = os.getenv("DB_USER", "habitt")
DB_PASSWORD = os.getenv("DB_PASSWORD", "habitt")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5436")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
