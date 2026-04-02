from unittest.mock import patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from tests.mocks import MockMQTTHandler

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def http_client():
    # Import here so main.py is already loaded — we patch the live instance
    from domain_gateway.main import app, internal_connections

    mock_mqtt = MockMQTTHandler()
    # Replace the connections list on the already-instantiated handler
    with patch.object(internal_connections, "connections", [mock_mqtt]):
        async with LifespanManager(app) as manager:
            async with AsyncClient(
                transport=ASGITransport(app=manager.app), base_url="http://testserver/"
            ) as client:
                yield client


# ── HTTP: /robots ─────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_get_robot_position_not_found(http_client: AsyncClient):
    response = await http_client.get("/robots/42/position")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_put_then_get_robot_position(http_client: AsyncClient):
    payload = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}

    put_response = await http_client.put("/robots/1/position", json=payload)
    assert put_response.status_code == 200

    body = put_response.json()
    assert body["forwarded_item"]["x"] == 1.0
    assert body["forwarded_item"]["y"] == 2.0
    assert body["forwarded_item"]["robot_id"] == 1

    get_response = await http_client.get("/robots/1/position")
    assert get_response.status_code == 200
    assert get_response.json()["x"] == 1.0


@pytest.mark.anyio
async def test_put_robot_position_invalid_payload(http_client: AsyncClient):
    response = await http_client.put("/robots/1/position", json={"x": 1.0})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_robot_position_different_robots_isolated(http_client: AsyncClient):
    payload = {"robot_id": 1, "x": 10.0, "y": 20.0, "orientation": 0.0}
    await http_client.put("/robots/1/position", json=payload)

    response = await http_client.get("/robots/2/position")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_not_implemented_endpoints(http_client: AsyncClient):
    for path in ["/robots/1/neighbors", "/robots/1/movement", "/robots/1/sensing"]:
        r = await http_client.get(path)
        assert r.status_code == 501, f"Expected 501 for GET {path}"
