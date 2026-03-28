import asyncio
from typing import override

from aiomqtt import Client

from domain_gateway.core.interfaces.handler import BaseHandler, MessageHandler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class MQTTHandler(BaseHandler, MessageHandler):
    def __init__(self):
        self.connections: list[BaseHandler] = []

    @override
    async def start(self, message_handler: MessageHandler) -> None:
        self._task = asyncio.create_task(self._listen())

    @override
    async def stop(self) -> None:
        if self._task:
            self._task.cancel()

    @override
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        raise NotImplementedError("To be implemented.")

    async def _listen(self) -> None:
        async with Client("broker.mqtt-dashboard.com") as client:
            await client.subscribe("esiot-2025-fgor")
            async for message in client.messages:
                self._dispatch(message)

    def _dispatch(self, message) -> None:
        print(message)
