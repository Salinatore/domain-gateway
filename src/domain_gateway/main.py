import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.connections.externals.connection import ExternalConnections
from domain_gateway.connections.externals.connections.coap.connection import (
    CoAPConnection,
)
from domain_gateway.connections.externals.connections.http.connection import (
    HTTPConnection,
)
from domain_gateway.connections.externals.connections.websocket.connection import (
    WebsocketConnection,
)
from domain_gateway.connections.internals.connection import InternalConnections
from domain_gateway.connections.internals.connections.mqtt.connection import (
    MQTTConnection,
)
from domain_gateway.core.bus import inbound_bus, outbound_bus
from domain_gateway.core.cache import cache

logging.basicConfig(level=logging.INFO)

cache.attach_bus(outbound_bus=outbound_bus)

external_connections = ExternalConnections(
    connections=[HTTPConnection(), WebsocketConnection(), CoAPConnection(cache=cache)]
)
internal_connections = InternalConnections(connections=[MQTTConnection()])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        external_connections.start(inbound_bus=inbound_bus, outbound_bus=outbound_bus),
        internal_connections.start(inbound_bus=inbound_bus, outbound_bus=outbound_bus),
    )
    yield
    await asyncio.gather(
        external_connections.stop(),
        internal_connections.stop(),
    )


description: str = """
Bridges external clients with the internal MQTT-based domain.

Inbound requests (HTTP, WebSocket, CoAP) are forwarded to the domain via the inbound bus.
Domain updates flow back through the outbound bus, updating the cache and notifying WebSocket subscribers.

> HTTP endpoints below cover REST-style reads and writes. For real-time updates, use the WebSocket (/ws) and subscription endpoints.
"""

app = FastAPI(
    title="Domain Gateway API",
    version="0.1.0",
    description=description,
    lifespan=lifespan,
)

app.include_router(external_connections.router)
app.include_router(internal_connections.router)
