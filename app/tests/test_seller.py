from httpx import AsyncClient

from app.tests import example

base_url = "/seller"


async def test_signup(client: AsyncClient):
    response = await client.post(
        f"{base_url}/signup",
        json={"name": "New Seller", "email": "new_seller@test.com", "password": "pass1234"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_seller@test.com"
    assert data["name"] == "New Seller"


async def test_signup_duplicate_email(client: AsyncClient):
    response = await client.post(
        f"{base_url}/signup",
        json={
            "name": example.SELLER["name"],
            "email": example.SELLER["email"],
            "password": example.SELLER["password"],
        },
    )
    assert response.status_code == 409


async def test_login(client: AsyncClient):
    response = await client.post(
        f"{base_url}/token",
        data={"username": example.SELLER["email"], "password": example.SELLER["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_invalid_password(client: AsyncClient):
    response = await client.post(
        f"{base_url}/token",
        data={"username": example.SELLER["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    response = await client.post(
        f"{base_url}/token",
        data={"username": "ghost@test.com", "password": "irrelevant"},
    )
    assert response.status_code == 401


async def test_logout(client: AsyncClient, seller_token: str):
    response = await client.get(
        f"{base_url}/logout",
        headers={"Authorization": f"Bearer {seller_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out"


async def test_protected_without_token(client: AsyncClient):
    response = await client.get(f"{base_url}/logout")
    assert response.status_code == 401
