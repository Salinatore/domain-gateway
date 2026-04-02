import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

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


@pytest.fixture
def test_client():
    """
    Sync TestClient — handles lifespan and WebSocket protocol natively.
    TestClient runs the async app in a background thread with its own event loop.
    """
    internal_connections.connections = [MockMQTTHandler()]
    with TestClient(
        app, base_url="http://testserver", raise_server_exceptions=True
    ) as client:
        yield client
    internal_connections.connections = []


# ── HTTP: subscriptions ───────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_create_subscription(http_client: AsyncClient):
    response = await http_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert body["subscribed_to_topic"] == "/robots/1/position"


@pytest.mark.anyio
async def test_read_subscription(http_client: AsyncClient):
    create = await http_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    sub_id = create.json()["id"]

    response = await http_client.get(f"/subscriptions/{sub_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sub_id
    assert response.json()["subscribed_to_topic"] == "/robots/1/position"


@pytest.mark.anyio
async def test_read_nonexistent_subscription(http_client: AsyncClient):
    import uuid

    response = await http_client.get(f"/subscriptions/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_subscription(http_client: AsyncClient):
    create = await http_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    sub_id = create.json()["id"]

    delete = await http_client.delete(f"/subscriptions/{sub_id}")
    assert delete.status_code == 204

    get = await http_client.get(f"/subscriptions/{sub_id}")
    assert get.status_code == 404


# ── WebSocket ─────────────────────────────────────────────────────────────────


def test_websocket_accepts_connection(test_client: TestClient):
    with test_client.websocket_connect("/ws/"):
        pass


def test_websocket_subscribe_message(test_client: TestClient):
    create = test_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    sub_id = create.json()["id"]

    with test_client.websocket_connect("/ws/") as ws:
        ws.send_json({"id": sub_id})
