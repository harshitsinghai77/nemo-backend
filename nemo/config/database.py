import os
from urllib.parse import quote

import databases
import sqlalchemy

DB_NAME = os.getenv("QOVERY_POSTGRESQL_Z794A99A3_DEFAULT_DATABASE_NAME", "nemo")
DB_USER = os.getenv("QOVERY_POSTGRESQL_Z794A99A3_LOGIN", "nemo")
DB_PASSWORD = os.getenv("QOVERY_POSTGRESQL_Z794A99A3_PASSWORD", "password")
DB_HOST = os.getenv("QOVERY_POSTGRESQL_Z794A99A3_HOST", "localhost")
DB_PORT = os.getenv("QOVERY_POSTGRESQL_Z794A99A3_PORT", "5432")
DB_MAX_SIZE = 10

environment = os.getenv("ENV", "development")

ENCODED_PASSWORD = quote(DB_PASSWORD)
DATABASE_URL = (
    f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
if environment == "development":
    DATABASE_URL = "postgresql://nemo:password@localhost:5432/nemo"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(DATABASE_URL)
