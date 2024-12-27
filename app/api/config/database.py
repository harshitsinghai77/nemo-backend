import os

# import databases
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

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
async_engine = create_async_engine(DATABASE_URL, pool_size=15, poolclass=QueuePool)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def close_connection():
    await async_engine.dispose()
