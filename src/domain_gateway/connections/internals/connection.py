import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.core.connection import Connection


class InternalConnections(Connection):
    """Composite connection that manages all internal protocol adapters (e.g. MQTT).

    Mirrors ``ExternalConnections`` but for the domain-side of the gateway.
    The bundled router is empty by default — internal protocols don't expose
    HTTP endpoints — but can be extended in future without changing the
    startup wiring.
    """

    def __init__(
        self,
        connections: list[Connection] | None = None,
    ):
        self._router = APIRouter()  # Empty router, as the ingress handler does not expose any HTTP/WS endpoint now but can in the future.
        self.connections: list[Connection] = connections or []

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    async def start(self) -> None:
        await asyncio.gather(*(connection.start() for connection in self.connections))

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self.connections))
