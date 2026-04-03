import asyncio
import logging
from typing import override

from aiomqtt import Client
from pydantic import ValidationError

from domain_gateway.core.bus import Bus
from domain_gateway.core.connection import Connection
from domain_gateway.models.topic.mappings import resolve_payload_class
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload
from domain_gateway.settings import settings

logger = logging.getLogger(__name__)

RECONNECT_DELAY: int = 2  # Seconds


class MQTTConnection(Connection):
    """Bridges the internal MQTT broker with the gateway message buses.

    Runs two long-lived background tasks:

    - **Listener**: subscribes to all MQTT topics (``/#``), parses incoming
      messages, and publishes them onto the outbound bus.
    - **Publisher**: drains an internal queue of (topic, payload) pairs
      produced by the inbound bus and forwards them to the broker.

    Both tasks reconnect automatically after any error, with a short delay
    defined by ``RECONNECT_DELAY``.
    """

    def __init__(self):
        self._listener_task: asyncio.Task | None = None
        self._publisher_task: asyncio.Task | None = None
        self._message_queue: asyncio.Queue[tuple[TopicPath, TopicPayload]] | None = None

        self._inbound_bus: Bus | None = None
        self._outbound_bus: Bus | None = None

        self._running: bool = False

    @override
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        self._running = True
        self._message_queue = asyncio.Queue()
        inbound_bus.subscribe(self._update)
        self._outbound_bus = outbound_bus

        self._listener_task = asyncio.create_task(
            self._listener(), name="mqtt-listener"
        )
        self._publisher_task = asyncio.create_task(
            self._publisher(), name="mqtt-publisher"
        )

    @override
    async def stop(self) -> None:
        self._running = False

        tasks = []
        if self._listener_task:
            self._listener_task.cancel()
            tasks.append(self._listener_task)
        if self._publisher_task:
            self._publisher_task.cancel()
            tasks.append(self._publisher_task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._listener_task = None
        self._publisher_task = None
        self._message_queue = None

    async def _update(self, topic: TopicPath, payload: TopicPayload) -> None:
        if self._running and self._message_queue is not None:
            await self._message_queue.put((topic, payload))

    async def _publisher(self) -> None:
        while self._running and self._message_queue is not None:
            try:
                async with Client(settings.mqtt_broker_url) as client:
                    while self._running:
                        topic, payload = await self._message_queue.get()
                        await client.publish(topic, payload=payload.model_dump_json())
            except Exception as e:
                logger.error("MQTT publisher error: %s", e)
                await asyncio.sleep(RECONNECT_DELAY)

    async def _listener(self) -> None:
        while self._running:
            try:
                async with Client(settings.mqtt_broker_url) as client:
                    await client.subscribe("/#")
                    async for message in client.messages:
                        if isinstance(message.payload, bytes):
                            await self._dispatch(
                                str(message.topic), message.payload.decode("utf-8")
                            )
                        else:
                            logger.error(
                                "Received non-string payload: %s", message.payload
                            )
            except Exception as e:
                logger.error("MQTT listener error: %s", e)
                await asyncio.sleep(RECONNECT_DELAY)

    async def _dispatch(self, topic: str, message: str) -> None:
        try:
            topic_payload = self._parse_message(topic, message)
            if self._outbound_bus is None:
                raise RuntimeError("Message bus is not initialized")
            await self._outbound_bus.publish(topic, topic_payload)
        except (ValidationError, ValueError) as e:
            logger.error("Invalid payload for topic %s: %s", topic, e)

    def _parse_message(self, topic: str, message: str) -> TopicPayload:
        payload_class = resolve_payload_class(topic)
        if payload_class is None:
            raise ValueError(f"No mapping found for topic: {topic}")
        return payload_class.model_validate_json(message)
