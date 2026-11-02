import os
import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

logger = logging.getLogger("hospital.database")

# Engine configuration
engine_kwargs = {"echo": False}
db_url = settings.async_database_url
if "sqlite" in db_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_async_engine(db_url, **engine_kwargs)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


_db_initialized = False
_init_lock = asyncio.Lock()


async def init_db():
    global _db_initialized
    if _db_initialized:
        return
    async with _init_lock:
        if _db_initialized:
            return
        logger.info("Initializing database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # On Vercel serverless (ephemeral SQLite), auto-seed demo records if users table is empty
        if os.environ.get("VERCEL"):
            try:
                from sqlalchemy import select, func
                from app.models.user import User
                async with async_session_maker() as session:
                    count = await session.scalar(select(func.count(User.id)))
                if not count:
                    from scripts.seed import seed
                    logger.info("Vercel serverless: auto-seeding demo clinical records...")
                    await seed(drop_first=False)
            except Exception as e:
                logger.warning(f"Vercel auto-seed notice: {e}")
                try:
                    from scripts.seed import seed
                    await seed(drop_first=False)
                except Exception as inner_e:
                    logger.error(f"Failed to seed Vercel database: {inner_e}")
        _db_initialized = True


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if not _db_initialized:
        await init_db()
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
