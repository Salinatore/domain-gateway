import pytest
from httpx import ASGITransport, AsyncClient

from domain_gateway.main import app


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://robots/"
    ) as ac:
        response = await ac.get("/12/position")
    assert response.status_code == 404
