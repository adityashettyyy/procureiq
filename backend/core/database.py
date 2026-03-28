from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        from models import quote_job, quote_result, supplier, rfq_draft  # noqa
        await conn.run_sync(Base.metadata.create_all)
    # Enable WAL mode for SQLite concurrency
    if "sqlite" in settings.database_url:
        async with AsyncSessionLocal() as session:
            await session.execute(__import__("sqlalchemy").text("PRAGMA journal_mode=WAL"))
            await session.commit()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
