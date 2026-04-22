import os
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Корень репозитория: .../backend/infrastructure/db/session.py → на 4 уровня вверх
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(_repo_root / ".env")

def _database_url() -> str:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")
    safe_user = quote_plus(user)
    safe_password = quote_plus(password)
    return f"postgresql+asyncpg://{safe_user}:{safe_password}@{host}:{port}/{db}"


DATABASE_URL = _database_url()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10
)

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI эндпоинтов.
    Обеспечивает получение и закрытие сессии БД.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
