import json

from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ARRAY
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

# --- SQLite compat: models use sqlalchemy.ARRAY (generic), not postgresql.ARRAY ---
SQLiteTypeCompiler.visit_ARRAY = lambda self, type_, **kw: "JSON"

_orig_bind = ARRAY.bind_processor
_orig_result = ARRAY.result_processor


def _array_bind(self, dialect):
    if dialect.name == "sqlite":
        return lambda value: json.dumps(value) if value is not None else None
    return _orig_bind(self, dialect)


def _array_result(self, dialect, coltype):
    if dialect.name == "sqlite":
        def process(value):
            if value is None:
                return None
            return json.loads(value) if isinstance(value, str) else value
        return process
    return _orig_result(self, dialect, coltype)


ARRAY.bind_processor = _array_bind
ARRAY.result_processor = _array_result

# --- App imports after patches ---
from unittest.mock import AsyncMock, MagicMock

from app.database.session import get_session
from app.main import app
from app.worker import tasks as worker_tasks
from app.tests import example
import app.database.redis as redis_module

# Mock Celery tasks (no broker in tests)
worker_tasks.add_log.delay = MagicMock()
worker_tasks.send_email_with_template.delay = MagicMock()
worker_tasks.send_mail.delay = MagicMock()

# Mock Redis (no Redis server in tests)
redis_module.add_jti_to_blacklist = AsyncMock()
redis_module.is_jti_blacklisted = AsyncMock(return_value=False)
redis_module.add_shipment_verification_code = AsyncMock()
redis_module.get_shipment_verification_code = AsyncMock(return_value=None)

engine = create_async_engine(url="sqlite+aiosqlite:///:memory:")
test_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session_override():
    async with test_session() as session:
        yield session

@pytest_asyncio.fixture(scope="session")
async def seller_token(client: AsyncClient):
    response = await client.post(
        "/seller/token",
        data={"username": example.SELLER["email"], "password": example.SELLER["password"]},
    )
    assert "access_token" in response.json()
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="session")
async def partner_token(client: AsyncClient):
    response = await client.post(
        "/partner/token",
        data={"username": example.DELIVERY_PARTNER["email"], "password": example.DELIVERY_PARTNER["password"]},
    )
    assert "access_token" in response.json()
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    print("🧪 setting up resources...")

    app.dependency_overrides[get_session] = get_session_override

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_session() as session:
        await example.create_test_data(session)
    yield

    app.dependency_overrides.clear()
    print(" ✅ tearing down resources...")
