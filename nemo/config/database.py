import os

import databases
import sqlalchemy

DB_NAME = os.getenv("DB_NAME", "nemo")
DB_USER = os.getenv("DB_USER", "nemo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_MAX_SIZE = 10
environment = os.getenv("ENV", "development")

QOVERY_URL = os.getenv(
    "QOVERY_POSTGRESQL_Z3BAA5944_DATABASE_URL",
    "Default QOVERY",
)
print("QOVERY: ", QOVERY_URL)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
if environment == "development":
    DATABASE_URL = "postgresql://nemo:password@localhost:5432/nemo"

database = databases.Database(QOVERY_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(QOVERY_URL)
