import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.core.connection import Connection
from domain_gateway.utils import include_routers


class ExternalConnections(Connection):
    """Composite connection that manages all external-facing protocol adapters.

    Aggregates HTTP, WebSocket, and CoAP connections under a single
    ``APIRouter`` and coordinates their lifecycle together.

    Example:
        external_connections = ExternalConnections(
            connections=[HTTPConnection(), WebsocketConnection(), CoAPConnection(cache=cache)]
        )
        await external_connections.start(inbound_bus, outbound_bus)
    """

    def __init__(
        self,
        connections: list[Connection] | None = None,
    ):
        self._router = APIRouter()
        self.connections: list[Connection] = connections or []
        include_routers(self._router, self.connections)

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    async def start(self) -> None:
        await asyncio.gather(*(connection.start() for connection in self.connections))

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self.connections))
