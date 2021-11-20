import os

# import databases
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, engine

DB_NAME = os.getenv("DB_NAME", "nemo")
DB_USER = os.getenv("DB_USER", "nemo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_MAX_SIZE = 10

environment = os.getenv("ENV", "development")

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
if environment == "development":
    DATABASE_URL = "postgresql+asyncpg://nemo:password@localhost:5432/nemo"

metadata = MetaData()
Base = declarative_base()
engine = create_async_engine(DATABASE_URL)
async_session = AsyncSession(bind=engine, expire_on_commit=True)


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
