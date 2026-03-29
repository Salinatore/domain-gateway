import asyncio
import logging
from typing import override

from aiomqtt import Client
from pydantic import ValidationError

from domain_gateway.core.interfaces.handler import Handler, MessageHandler
from domain_gateway.models.topic.mappings import resolve_payload_class
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

logger = logging.getLogger(__name__)


class MQTTHandler(Handler):
    def __init__(self):
        self._task: asyncio.Task | None = None

    @override
    async def start(self, message_handler: MessageHandler) -> None:
        self.message_handler: MessageHandler = message_handler
        self._task = asyncio.create_task(self._listen())

    @override
    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    @override
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        asyncio.create_task(self._publish(str(topic), payload.model_dump_json()))

    async def _listen(self) -> None:
        async with Client("localhost") as client:
            await client.subscribe("/#")
            async for message in client.messages:
                if isinstance(message.payload, bytes):
                    self._dispatch(str(message.topic), message.payload.decode("utf-8"))
                else:
                    logger.error("Received non-string payload: %s", message.payload)

    async def _publish(self, topic: str, payload: str) -> None:
        async with Client("localhost") as client:
            await client.publish(topic, payload=payload)

    def _dispatch(self, topic: str, message: str) -> None:
        try:
            topic_payload = self._parse_message(topic, message)
            self.message_handler.update(topic, topic_payload)
        except (ValidationError, ValueError) as e:
            logger.error("Invalid payload for topic %s: %s", topic, e)

    def _parse_message(self, topic: str, message: str) -> TopicPayload:
        payload_class = resolve_payload_class(topic)
        if payload_class is None:
            raise ValueError(f"No mapping found for topic: {topic}")
        return payload_class.model_validate_json(message)
