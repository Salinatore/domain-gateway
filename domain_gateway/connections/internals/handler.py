import asyncio
from typing import override

from fastapi import APIRouter

from domain_gateway.connections.internals.connections.mqtt.handler import MQTTHandler
from domain_gateway.core.interfaces.handler import (
    Handler,
    MessageHandler,
)
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class InternalConnectionsHandler(Handler):
    def __init__(self):
        self._router = APIRouter()  # Empty router, as the ingress handler does not expose any HTTP/WS endpoint now but can in the future.
        self.connections: list[Handler] = [
            MQTTHandler(),
        ]

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
        for connection in self.connections:
            connection.update(topic, payload)
