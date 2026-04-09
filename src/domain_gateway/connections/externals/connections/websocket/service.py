# src/domain_gateway/connections/externals/connections/websocket/service.py
import asyncio
import logging
from typing import Protocol
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from starlette import status

from domain_gateway.connections.externals.connections.websocket.models.ws import (
    PublishMessage,
    SubscriptionMessage,
    SubscriptionUpdateMessage,
    client_sent_message_adapter,
)
from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

logger = logging.getLogger(__name__)


class WebSocketManager(Protocol):
    async def add(self, websocket: WebSocket) -> None:
        """Accept and serve a WebSocket connection until it closes."""


class SubscriptionManager(Protocol):
    def create_subscription(self, topic: TopicPath) -> UUID: ...
    def delete_subscription(self, subscription_id: UUID) -> None: ...
    def get_topic_from_subscription(
        self, subscription_id: UUID
    ) -> TopicPath | None: ...


class WebSocketService:
    def __init__(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        self._inbound_bus = inbound_bus
        self._outbound_bus = outbound_bus

        self._topic_subscriptions_dict: dict[TopicPath, list[UUID]] = {}
        self._subscription_websocket_dict: dict[UUID, WebSocket] = {}

        self._active_tasks: set[asyncio.Task] = set()
        self._running = False

    async def start(self) -> None:
        """Start the service (subscribe to outbound bus)."""
        self._running = True
        self._outbound_bus.subscribe(self._handle_incoming_update)

    async def stop(self) -> None:
        """Cancel all active connection tasks and clean up."""
        self._running = False
        for task in self._active_tasks:
            task.cancel()
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
        self._active_tasks.clear()

    async def add(self, websocket: WebSocket) -> None:
        if not self._running:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            return

        await websocket.accept()
        task = asyncio.current_task()
        if task:
            self._active_tasks.add(task)
        try:
            while self._running:
                try:
                    data = await websocket.receive_json()
                    logger.debug("Received data from websocket: %s", data)
                    message = client_sent_message_adapter.validate_python(data)

                    match message:
                        case SubscriptionMessage():
                            for _, id_list in self._topic_subscriptions_dict.items():
                                if message.id in id_list:
                                    self._subscription_websocket_dict[message.id] = (
                                        websocket
                                    )
                        case PublishMessage():
                            await self._inbound_bus.publish(
                                message.topic, message.payload
                            )

                except WebSocketDisconnect:
                    break
                except ValidationError as e:
                    await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                    logger.error("Invalid message received: %s", e)
                    break
                except Exception as e:
                    await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
                    logger.error("Error receiving data: %s", e)
                    break
        finally:
            if task:
                self._active_tasks.discard(task)

    def create_subscription(self, topic: TopicPath) -> UUID:
        subscription_id = uuid4()

        if topic not in self._topic_subscriptions_dict:
            self._topic_subscriptions_dict[topic] = []
        self._topic_subscriptions_dict[topic].append(subscription_id)

        return subscription_id

    def delete_subscription(self, subscription_id: UUID) -> None:
        self._subscription_websocket_dict.pop(subscription_id, None)
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                subscription_ids.remove(subscription_id)
                if not subscription_ids:
                    del self._topic_subscriptions_dict[topic]
                break

    def get_topic_from_subscription(self, subscription_id: UUID) -> TopicPath | None:
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                return topic
        return None

    async def _handle_incoming_update(
        self, topic: TopicPath, payload: TopicPayload
    ) -> None:
        if topic not in self._topic_subscriptions_dict:
            return

        await asyncio.gather(
            *[
                websocket.send_text(
                    SubscriptionUpdateMessage(
                        subscription_id=subscription_id,
                        topic=topic,
                        payload=payload,
                    ).model_dump_json()
                )
                for subscription_id in self._topic_subscriptions_dict[topic]
                if (websocket := self._subscription_websocket_dict.get(subscription_id))
            ],
            return_exceptions=True,
        )
