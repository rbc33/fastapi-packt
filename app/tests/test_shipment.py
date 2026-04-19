from httpx import AsyncClient

from app.tests import example
from app.database.models import TagName

base_url = "/shipment/"


# ── GET /shipment/ ────────────────────────────────────────────────────────────

async def test_get_shipment(client: AsyncClient):
    response = await client.get(base_url, params={"id": str(example.TEST_SHIPMENT_ID)})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(example.TEST_SHIPMENT_ID)
    assert data["content"] == example.SHIPMENT["content"]


async def test_get_shipment_not_found(client: AsyncClient):
    response = await client.get(base_url, params={"id": "00000000-0000-0000-0000-000000000000"})
    assert response.status_code == 404


# ── POST /shipment/ ───────────────────────────────────────────────────────────

async def test_submit_shipment_no_auth(client: AsyncClient):
    response = await client.post(base_url, json=example.SHIPMENT)
    assert response.status_code == 401


async def test_submit_shipment(client: AsyncClient, seller_token: str):
    response = await client.post(
        base_url,
        json=example.SHIPMENT,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == example.SHIPMENT["content"]
    assert len(data["timeline"]) == 1
    assert data["timeline"][0]["status"] == "placed"


# ── PATCH /shipment/ ──────────────────────────────────────────────────────────

async def test_update_shipment(client: AsyncClient, seller_token: str, partner_token: str):
    # Create a fresh shipment to update
    create = await client.post(
        base_url,
        json=example.SHIPMENT,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert create.status_code == 201
    shipment_id = create.json()["id"]

    response = await client.patch(
        base_url,
        params={"id": shipment_id},
        json={"status": "in_transit", "location": example.SHIPMENT["destination"]},
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert response.status_code == 200


async def test_update_shipment_no_auth(client: AsyncClient):
    response = await client.patch(
        base_url,
        params={"id": str(example.TEST_SHIPMENT_ID)},
        json={"status": "in_transit"},
    )
    assert response.status_code == 401


async def test_update_shipment_empty(client: AsyncClient, seller_token: str, partner_token: str):
    create = await client.post(
        base_url,
        json=example.SHIPMENT,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    shipment_id = create.json()["id"]

    response = await client.patch(
        base_url,
        params={"id": shipment_id},
        json={},
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert response.status_code == 400


# ── GET /shipment/cancel ──────────────────────────────────────────────────────

async def test_cancel_shipment(client: AsyncClient, seller_token: str):
    create = await client.post(
        base_url,
        json=example.SHIPMENT,
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert create.status_code == 201
    shipment_id = create.json()["id"]

    response = await client.get(
        f"{base_url}cancel",
        params={"id": shipment_id},
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["timeline"][-1]["status"] == "cancelled"


async def test_cancel_shipment_no_auth(client: AsyncClient):
    response = await client.get(
        f"{base_url}cancel",
        params={"id": str(example.TEST_SHIPMENT_ID)},
    )
    assert response.status_code == 401


# ── GET /shipment/tag  (add tag) ──────────────────────────────────────────────

async def test_add_tag(client: AsyncClient):
    response = await client.get(
        f"{base_url}tag",
        params={"id": str(example.TEST_SHIPMENT_ID), "tag_name": TagName.EXPRESS.value},
    )
    assert response.status_code == 200
    tags = [t["name"] for t in response.json()["tags"]]
    assert TagName.EXPRESS.value in tags


# ── GET /shipment/tagged ──────────────────────────────────────────────────────

async def test_get_by_tag(client: AsyncClient):
    response = await client.get(
        f"{base_url}tagged",
        params={"tag_name": TagName.EXPRESS.value},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── DELETE /shipment/tag ──────────────────────────────────────────────────────

async def test_remove_tag(client: AsyncClient):
    response = await client.delete(
        f"{base_url}tag",
        params={"id": str(example.TEST_SHIPMENT_ID), "tag_name": TagName.EXPRESS.value},
    )
    assert response.status_code == 200
    tags = [t["name"] for t in response.json()["tags"]]
    assert TagName.EXPRESS.value not in tags
