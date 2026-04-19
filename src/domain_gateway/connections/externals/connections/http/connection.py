from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.http.routers.computing import (
    ComputingRouter,
)
from domain_gateway.connections.externals.connections.http.routers.robots import (
    RobotRouter,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.core.connection import Connection


class HTTPConnection(Connection):
    def __init__(
        self, root_router: APIRouter, cache: Cache, inbound_bus: Bus, outbound_bus: Bus
    ):
        root_router.include_router(
            RobotRouter(cache=cache, inbound_bus=inbound_bus).router
        )
        root_router.include_router(
            ComputingRouter(cache=cache, inbound_bus=inbound_bus).router
        )

    @override
    async def start(self) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass
