import pytest
from starlette.testclient import TestClient

from domain_gateway.core.container import Container
from domain_gateway.core.monitor import Status
from domain_gateway.main import create_app
from tests.mocks.connections import MockMQTTConnection


@pytest.fixture
def container():
    c = Container()
    c._internal_connections._connections = [
        MockMQTTConnection(c._inbound_bus, c._outbound_bus)
    ]

    return c


@pytest.fixture
def test_client(container):
    container._internal_connections._mqtt_health_handle.report(Status.UP)
    app = create_app(container)
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture
def unhealthy_client(container):
    # Left unhealthy on purpose.
    app = create_app(container)
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
