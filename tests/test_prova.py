import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from domain_gateway.main import app


@pytest.fixture
async def client():
    """Create a test client with proper lifespan event handling."""
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://robots/"
        ) as client:
            yield client


@pytest.mark.anyio
async def test_root(client: AsyncClient):
    response = await client.get("/12/position")
    assert response.status_code == 404
