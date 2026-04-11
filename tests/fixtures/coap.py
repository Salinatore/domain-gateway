import socket

import aiocoap
import aiocoap.resource as resource
import pytest

from domain_gateway.connections.externals.connections.coap.resources.computing import (
    FormationResource,
    LeaderResource,
)
from domain_gateway.connections.externals.connections.coap.resources.robots import (
    RobotsSubsite,
)
from domain_gateway.core.container import Container


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def coap_port():
    return get_free_port()


@pytest.fixture
async def coap_server(container: Container, coap_port: int):
    # Start the container so MockMQTTConnection.start() subscribes its echo
    # callback to the inbound bus — without this the cache never gets written.
    await container.internal_connections.start()

    site = resource.Site()
    site.add_resource(
        ["robots"],
        RobotsSubsite(
            container._cache,
            container._inbound_bus,
            container._outbound_bus,
        ),
    )
    site.add_resource(
        ["computing", "inputs", "formation"],
        FormationResource(
            container._cache,
            container._inbound_bus,
            container._outbound_bus,
        ),
    )
    site.add_resource(
        ["computing", "inputs", "leader"],
        LeaderResource(
            container._cache,
            container._inbound_bus,
            container._outbound_bus,
        ),
    )

    ctx = await aiocoap.Context.create_server_context(
        site, bind=("127.0.0.1", coap_port)
    )
    yield ctx

    await ctx.shutdown()
    await container.internal_connections.stop()


@pytest.fixture
async def coap_client(coap_server):
    ctx = await aiocoap.Context.create_client_context()
    yield ctx
    await ctx.shutdown()
