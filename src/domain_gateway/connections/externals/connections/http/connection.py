from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.http.routers.computing import (
    computing_inputs_router,
)
from domain_gateway.connections.externals.connections.http.routers.robots import (
    robots_router,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.connection import Connection


class HTTPConnection(Connection):
    def __init__(self):
        self._router = APIRouter()
        self._router.include_router(robots_router)
        self._router.include_router(computing_inputs_router)

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    @override
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass
