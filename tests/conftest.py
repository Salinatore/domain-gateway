# tests/conftest.py
import pytest
from starlette.testclient import TestClient

from domain_gateway.connections.externals.connection import ExternalConnections
from domain_gateway.connections.externals.connections.http.connection import (
    HTTPConnection,
)
from domain_gateway.connections.externals.connections.websocket.connection import (
    WebsocketConnection,
)
from domain_gateway.connections.internals.connection import InternalConnections
from domain_gateway.dependencies.container import Container
from domain_gateway.main import create_app
from tests.mocks import MockMQTTConnection


@pytest.fixture
def container():
    c = Container()
    c._internal_connections = InternalConnections(
        connections=[MockMQTTConnection(c._inbound_bus, c._outbound_bus)],
        inbound_bus=c._inbound_bus,
        outbound_bus=c._outbound_bus,
    )
    c._external_connections = ExternalConnections(
        connections=[
            HTTPConnection(c._inbound_bus, c._outbound_bus),
            WebsocketConnection(c._inbound_bus, c._outbound_bus),
        ],
        inbound_bus=c._inbound_bus,
        outbound_bus=c._outbound_bus,
    )
    return c


@pytest.fixture
def test_client(container):
    app = create_app(container)
    # No dependency_overrides needed — routes read from app.state.container
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
