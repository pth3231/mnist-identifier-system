import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.app.main import app
from src.app.database import Base, get_db
from src.app.models.schemas import UserCreate, UserLogin

pytest_plugins = ("pytest_asyncio",)

# Test database setup
DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(DATABASE_URL_TEST, echo=False, future=True)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        session = async_session_maker()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield async_session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
