from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.websocket.routers.subscription import (
    WebsocketSubscriptionRouter,
)
from domain_gateway.connections.externals.connections.websocket.routers.ws import (
    WebsocketEndpointRouter,
)
from domain_gateway.connections.externals.connections.websocket.service import (
    WebSocketService,
)
from domain_gateway.core.connection import Bus, Connection


class WebsocketConnection(Connection):
    def __init__(self, inbound_bus: Bus, outbound_bus: Bus):
        self._websocket_service: WebSocketService = WebSocketService(
            inbound_bus=inbound_bus,
            outbound_bus=outbound_bus,
        )

        self._router = APIRouter()
        self._router.include_router(
            WebsocketSubscriptionRouter(
                subscription_manager=self._websocket_service,
            ).router
        )
        self._router.include_router(
            WebsocketEndpointRouter(
                websocket_manager=self._websocket_service,
            ).router
        )

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    @override
    async def start(self) -> None:
        await self._websocket_service.start()

    @override
    async def stop(self) -> None:
        await self._websocket_service.stop()
