from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.websocket.routers.subscription import (
    subscription_router,
)
from domain_gateway.connections.externals.connections.websocket.service import (
    webscoket_service,
)
from domain_gateway.core.handler import Bus, Handler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class WebsocketHandler(Handler):
    def __init__(self):
        self._router = APIRouter()
        self._router.include_router(subscription_router)

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    @override
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        webscoket_service.set_buses(inbound=inbound_bus, outbound=outbound_bus)

    @override
    async def stop(self) -> None:
        pass

    @override
    async def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        pass
