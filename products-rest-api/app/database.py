"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Base class for models — importable without creating a live engine
Base = declarative_base()

# Module-level references; populated on first use via _get_engine()
_engine = None
_async_session = None


def _get_engine():
    """Return (and lazily create) the shared async engine."""
    global _engine, _async_session
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=True,
        )
        _async_session = sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _engine, _async_session


async def init_db() -> None:
    """Initialize database tables."""
    engine, _ = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session for dependency injection."""
    _, session_factory = _get_engine()
    async with session_factory() as session:
        yield session


async def close_db() -> None:
    """Close database connection."""
    engine, _ = _get_engine()
    await engine.dispose()
