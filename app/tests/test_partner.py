from httpx import AsyncClient

from app.tests import example

base_url = "/partner"


async def test_signup(client: AsyncClient):
    response = await client.post(
        f"{base_url}/signup",
        json={
            "name": "New Partner",
            "email": "new_partner@test.com",
            "password": "pass1234",
            "serviceable_zip_codes": [20001, 20002],
            "max_handling_capacity": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_partner@test.com"


async def test_signup_duplicate_email(client: AsyncClient):
    response = await client.post(
        f"{base_url}/signup",
        json={
            "name": example.DELIVERY_PARTNER["name"],
            "email": example.DELIVERY_PARTNER["email"],
            "password": example.DELIVERY_PARTNER["password"],
            "serviceable_zip_codes": example.DELIVERY_PARTNER["serviceable_zip_codes"],
            "max_handling_capacity": example.DELIVERY_PARTNER["max_handling_capacity"],
        },
    )
    assert response.status_code == 409


async def test_login(client: AsyncClient):
    response = await client.post(
        f"{base_url}/token",
        data={
            "username": example.DELIVERY_PARTNER["email"],
            "password": example.DELIVERY_PARTNER["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_invalid(client: AsyncClient):
    response = await client.post(
        f"{base_url}/token",
        data={"username": example.DELIVERY_PARTNER["email"], "password": "wrong"},
    )
    assert response.status_code == 401


async def test_update(client: AsyncClient, partner_token: str):
    response = await client.post(
        f"{base_url}/",
        json={"max_handling_capacity": 10},
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert response.status_code == 200
    assert response.json()["max_handling_capacity"] == 10


async def test_update_no_fields(client: AsyncClient, partner_token: str):
    response = await client.post(
        f"{base_url}/",
        json={},
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert response.status_code == 400


async def test_update_unauthorized(client: AsyncClient):
    response = await client.post(f"{base_url}/", json={"max_handling_capacity": 5})
    assert response.status_code == 401


async def test_logout(client: AsyncClient, partner_token: str):
    response = await client.get(
        f"{base_url}/logout",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out"
