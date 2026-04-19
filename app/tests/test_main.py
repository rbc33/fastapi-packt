from httpx import AsyncClient

from app.tests import example
from app.utils import print_label

# @pytest.mark.asyncio
async def test_app(client: AsyncClient):
    response = await client.get("/shipment/?id=343a57d5-e1c0-4fdb-adfd-b4926f0e1b33")
    print("[ Status ]", response.status_code)
    print("[ Body   ]", response.text)
    assert response.status_code == 200

async def test_seller_login(client: AsyncClient):
    response = await client.post(
        "/seller/token",
        data={"username": example.SELLER["email"], "password": example.SELLER["password"]}
    )
    print_label(response.json())
    print("[ Status ]", response.status_code)
    print("[ Body   ]", response.text)
    assert response.status_code == 200
