import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.core.bus import Bus
from domain_gateway.core.handler import Handler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class InternalConnectionsHandler(Handler):
    def __init__(self, connections: list[Handler] | None = None):
        self._router = APIRouter()  # Empty router, as the ingress handler does not expose any HTTP/WS endpoint now but can in the future.
        self.connections: list[Handler] = connections or []

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
