import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.core.bus import Bus
from domain_gateway.core.connection import Connection
from domain_gateway.utils import include_routers


class ExternalConnections(Connection):
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

    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        await asyncio.gather(
            *(
                connection.start(inbound_bus, outbound_bus)
                for connection in self.connections
            )
        )

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self.connections))
