import pytest
from starlette.testclient import TestClient

from domain_gateway.main import app, internal_connections
from tests.mocks import MockMQTTConnection


@pytest.fixture
def test_client():
    """
    Sync TestClient — handles lifespan and WebSocket protocol natively.
    TestClient runs the async app in a background thread with its own event loop.
    """
    internal_connections.connections = [MockMQTTConnection()]
    with TestClient(
        app, base_url="http://testserver", raise_server_exceptions=True
    ) as client:
        yield client
    internal_connections.connections = []
