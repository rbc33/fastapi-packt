import json
from datetime import datetime, timedelta
from uuid import UUID, uuid4

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
from unittest.mock import MagicMock

from app.database.session import get_session
from app.main import app
from app.database.models import Seller, DeliveryPartner, Shipment, ShipmentEvent, ShipmentStatus
from app.worker import tasks as worker_tasks

worker_tasks.add_log.delay = MagicMock()

# Fixed IDs for deterministic tests
TEST_SHIPMENT_ID = UUID("343a57d5-e1c0-4fdb-adfd-b4926f0e1b33")

engine = create_async_engine(url="sqlite+aiosqlite:///:memory:")
test_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session_override():
    async with test_session() as session:
        yield session


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
        seller = Seller(
            id=uuid4(),
            name="Test Seller",
            email="seller@test.com",
            password_hash="hashed",
            created_at=datetime.now(),
        )
        partner = DeliveryPartner(
            id=uuid4(),
            name="Test Partner",
            email="partner@test.com",
            password_hash="hashed",
            serviceable_zip_codes=[10001, 10002],
            max_handling_capacity=10,
            created_at=datetime.now(),
        )
        session.add(seller)
        session.add(partner)
        await session.commit()
        await session.refresh(seller)
        await session.refresh(partner)

        shipment = Shipment(
            id=TEST_SHIPMENT_ID,
            content="Test Package",
            weight=2.5,
            destination=10001,
            client_contact_email="client@test.com",
            client_contact_phone=None,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
            delivery_partner_id=partner.id,
            created_at=datetime.now(),
        )
        session.add(shipment)
        await session.commit()

        event = ShipmentEvent(
            id=uuid4(),
            location=10001,
            status=ShipmentStatus.placed,
            shipment_id=TEST_SHIPMENT_ID,
            created_at=datetime.now(),
        )
        session.add(event)
        await session.commit()

    yield

    app.dependency_overrides.clear()
    print(" ✅ tearing down resources...")
