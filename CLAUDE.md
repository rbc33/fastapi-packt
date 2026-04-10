# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
fastapi dev app/main.py
```

API docs are available at `/docs` (Swagger) and `/scalar` (Scalar UI).

## Database migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "description"

# Stamp DB to a revision without running it (e.g. when DB is already in sync)
alembic stamp <revision_id>
```

**Important:** `app/database/session.py` calls `SQLModel.metadata.create_all` on startup, which means tables may already exist when Alembic runs. When autogenerate produces an empty migration, the DB is likely already in sync — use `alembic stamp head`. When writing migrations that touch existing enums, use `create_type=False` on `postgresql.ENUM`.

## Architecture

This is a FastAPI + SQLModel + PostgreSQL app for a shipment management system with three actors: **Sellers**, **DeliveryPartners**, and their **Shipments**.

### Request flow

```
Router (app/api/routers/) → Service (app/services/) → DB (via AsyncSession)
```

- **Routers** handle HTTP, extract typed dependencies, delegate to services
- **Services** contain business logic; each domain class extends `BaseService` (or `UserService` for auth-bearing entities)
- **Dependencies** (`app/api/dependencies.py`) wire services and auth via FastAPI `Depends` — `SellerDep`, `DeliveryPartnerDep`, `ShipmentServiceDep`, etc. are `Annotated` type aliases used directly in route signatures

### Auth pattern

Two separate OAuth2 flows — one for sellers (`/seller/token`), one for partners (`/partner/token`). Tokens are JWTs (PyJWT, HS256 by default). Logout is implemented via a Redis JTI blacklist (`app/database/redis.py`). Token generation/validation lives in `app/utils.py` and `app/core/security.py`.

### Models (`app/database/models.py`)

- `User` (non-table base) → `Seller`, `DeliveryPartner`
- `Shipment` has no `status` column — status is derived from the last `ShipmentEvent` in its `timeline` relationship (`shipment.status` is a `@property`)
- `ShipmentEvent` holds the `ShipmentStatus` enum column and is append-only

### Configuration

Loaded from `.env` via `pydantic-settings`. Required vars:

```
DATABASE_URL=postgresql+asyncpg://...
REDIS_HOST=...
REDIS_PORT=...
JWT_SECRET=...
JWT_ALGORITHM=HS256
```
