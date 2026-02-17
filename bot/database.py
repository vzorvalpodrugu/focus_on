import asyncio

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base
import dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

DB_USER=os.getenv("DB_USER")
DB_PASS=os.getenv("DB_PASS")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_db():
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        database='postgres'
    )

    try:
        exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")

        if exists:
            raise logger.info("Database has been created early")

        elif not exists:
            try:
                await conn.execute(f'CREATE DATABASE {DB_NAME};')
                logger.info('Database has been created!✅')
            except Exception as e:
                logger.error(f'Database has not been created. Error: {e}')
                raise
    except Exception as e:
        logger.error(f'Bad request to database. Error: {e}')
        raise

    await conn.close()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info('Tables has been created!✅')
    except Exception as e:
        logger.error(f'Tables has not been created. Error: {e}')
        raise

async def main():
    await create_db()
    await init_db()

if __name__ == '__main__':
    asyncio.run(main())