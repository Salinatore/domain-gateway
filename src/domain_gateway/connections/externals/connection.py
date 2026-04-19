import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.coap.connection import (
    CoAPConnection,
)
from domain_gateway.connections.externals.connections.http.connection import (
    HTTPConnection,
)
from domain_gateway.connections.externals.connections.websocket.connection import (
    WebsocketConnection,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.core.connection import Connection
from domain_gateway.core.monitor import HealthMonitor


class ExternalConnections(Connection):
    """Composite connection that manages all external-facing protocol adapters."""

    def __init__(
        self,
        inbound_bus: Bus,
        outbound_bus: Bus,
        health_monitor: HealthMonitor,
        root_router: APIRouter,
        cache: Cache,
    ):
        coap_health_handle = health_monitor.register(CoAPConnection, critical=False)
        self._connections: list[Connection] = [
            HTTPConnection(
                root_router=root_router,
                cache=cache,
                inbound_bus=inbound_bus,
                outbound_bus=outbound_bus,
                health_checkable=health_monitor,
            ),
            WebsocketConnection(
                root_router=root_router,
                inbound_bus=inbound_bus,
                outbound_bus=outbound_bus,
            ),
            CoAPConnection(
                health_handle=coap_health_handle,
                cache=cache,
                inbound_bus=inbound_bus,
                outbound_bus=outbound_bus,
            ),
        ]

    async def start(self) -> None:
        await asyncio.gather(*(connection.start() for connection in self._connections))

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self._connections))
