import os

import databases
import sqlalchemy

DB_NAME = os.getenv("DB_NAME", "nemo")
DB_USER = os.getenv("DB_USER", "nemo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5436")
DB_MAX_SIZE = 10

environment = os.getenv("ENV", "development")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
if environment == "development":
    DATABASE_URL = "postgresql://nemo:password@localhost:5432/nemo"

database = databases.Database(DATABASE_URL + f"?min_size=1&max_size={DB_MAX_SIZE}")
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
