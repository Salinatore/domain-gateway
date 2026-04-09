from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.websocket.routers.subscription import (
    subscription_router,
)
from domain_gateway.connections.externals.connections.websocket.routers.ws import (
    ws_router,
)
from domain_gateway.core.connection import Bus, Connection


class WebsocketConnection(Connection):
    def __init__(self, inbound_bus: Bus, outbound_bus: Bus):
        super().__init__(inbound_bus=inbound_bus, outbound_bus=outbound_bus)
        self._router = APIRouter()
        self._router.include_router(subscription_router)
        self._router.include_router(ws_router)

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    @override
    async def start(self) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass
