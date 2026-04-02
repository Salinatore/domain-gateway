import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from domain_gateway.main import app, internal_connections
from tests.mocks import MockMQTTHandler

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def http_client():
    internal_connections.connections = [MockMQTTHandler()]
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://testserver/"
        ) as client:
            yield client
    internal_connections.connections = []


# ── HTTP: robots ──────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_robot_position_not_found(http_client: AsyncClient):
    """Cache is empty on startup — should return 404."""
    response = await http_client.get("/robots/42/position")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_put_robot_position_returns_correct_body(http_client: AsyncClient):
    """PUT should return the forwarded item in the response body."""
    payload = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}

    response = await http_client.put("/robots/1/position", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["forwarded_item"]["x"] == 1.0
    assert body["forwarded_item"]["y"] == 2.0
    assert body["forwarded_item"]["robot_id"] == 1
    assert "forwarded_to_topic" in body
    assert "forwarded_at" in body


@pytest.mark.anyio
async def test_put_then_get_robot_position(http_client: AsyncClient):
    """PUT publishes to inbound bus → mock echoes to outbound → cache stores it → GET returns it."""
    payload = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}

    await http_client.put("/robots/1/position", json=payload)

    response = await http_client.get("/robots/1/position")
    assert response.status_code == 200
    body = response.json()
    assert body["x"] == 1.0
    assert body["y"] == 2.0
    assert body["robot_id"] == 1


@pytest.mark.anyio
async def test_put_robot_position_updates_cache(http_client: AsyncClient):
    """A second PUT should overwrite the first in the cache."""
    first = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}
    second = {"robot_id": 1, "x": 99.0, "y": 99.0, "orientation": 1.0}

    await http_client.put("/robots/1/position", json=first)
    await http_client.put("/robots/1/position", json=second)

    response = await http_client.get("/robots/1/position")
    assert response.status_code == 200
    assert response.json()["x"] == 99.0


@pytest.mark.anyio
async def test_put_robot_position_invalid_payload(http_client: AsyncClient):
    """Missing required fields should return 422 Unprocessable Entity."""
    response = await http_client.put("/robots/1/position", json={"x": 1.0})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_robots_are_isolated(http_client: AsyncClient):
    """Position stored for robot 1 should not affect robot 2."""
    payload = {"robot_id": 1, "x": 10.0, "y": 20.0, "orientation": 0.0}
    await http_client.put("/robots/1/position", json=payload)

    response = await http_client.get("/robots/2/position")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_not_implemented_endpoints(http_client: AsyncClient):
    """Endpoints not yet implemented should return 501."""
    for path in ["/robots/1/neighbors", "/robots/1/movement", "/robots/1/sensing"]:
        response = await http_client.get(path)
        assert response.status_code == 501, f"Expected 501 for GET {path}"
