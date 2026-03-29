import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.cache.base import Cache
from domain_gateway.connections.externals.connections.http.handler import HTTPHandler
from domain_gateway.connections.externals.connections.websocket.handler import (
    WebsocketHandler,
)
from domain_gateway.core.interfaces.handler import Handler, MessageHandler
from domain_gateway.core.utils.utils import include_routers
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


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

    @override
    async def start(self, message_handler: MessageHandler) -> None:
        await asyncio.gather(
            *(connection.start(message_handler) for connection in self.connections)
        )

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self.connections))

    @override
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        self._cache.set(topic, payload)
        for connection in self.connections:
            connection.update(topic, payload)
