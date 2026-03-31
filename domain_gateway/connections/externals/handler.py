import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.connections.externals.connections.http.handler import HTTPHandler
from domain_gateway.connections.externals.connections.websocket.handler import (
    WebsocketHandler,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.core.handler import Handler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload
from domain_gateway.utils import include_routers


class ExternalConnectionsHandler(Handler):
    def __init__(self, cache: Cache):
        self._cache = cache
        self._router = APIRouter()
        self.connections: list[Handler] = [
            HTTPHandler(),
            WebsocketHandler(),
        ]
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

    @override
    async def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        asyncio.gather(
            *(connection.update(topic, payload) for connection in self.connections)
        )
