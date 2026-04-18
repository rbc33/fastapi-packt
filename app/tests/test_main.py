from httpx import AsyncClient
# @pytest.mark.asyncio
async def test_app(client: AsyncClient):
    response = await client.get("/shipment?id=343a57d5-e1c0-4fdb-adfd-b4926f0e1b33")
    print("[ Status ]", response.status_code)
    print("[ Body   ]", response.text)
    assert response.status_code == 200

