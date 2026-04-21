import asyncio
import logging
from typing import Protocol
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

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
    """Protocol for objects that can accept and serve WebSocket connections."""

    async def add(self, websocket: WebSocket) -> None:
        """Accept and serve a WebSocket connection until it closes.

        Args:
            websocket: The incoming WebSocket connection to manage.
        """


class SubscriptionManager(Protocol):
    """Protocol for objects that manage topic subscriptions for WebSocket clients.

    A subscription links a topic path to a UUID that a client can later
    associate with a live WebSocket connection to receive push updates.
    """

    def create_subscription(self, topic: TopicPath) -> UUID:
        """Create a new subscription for the given topic.

        Args:
            topic: The topic path the client wishes to subscribe to.

        Returns:
            A unique subscription ID the client should use to identify itself.
        """
        ...

    def delete_subscription(self, subscription_id: UUID) -> None:
        """Remove a subscription and discard its associated WebSocket mapping.

        Args:
            subscription_id: The ID of the subscription to remove.
        """
        ...

    def get_topic_from_subscription(self, subscription_id: UUID) -> TopicPath | None:
        """Resolve the topic path associated with a subscription ID.

        Args:
            subscription_id: The subscription ID to look up.

        Returns:
            The corresponding ``TopicPath``, or ``None`` if not found.
        """
        ...


class WebSocketService:
    """Manages WebSocket connections, subscriptions, and message routing.

    Serves as the concrete implementation of both ``WebSocketManager`` and
    ``SubscriptionManager``. Clients follow a two-step flow:

    1. **Subscribe** — POST to the subscription endpoint to receive a UUID
       linked to a topic of interest.
    2. **Connect** — open a WebSocket and send a ``SubscriptionMessage``
       containing the UUID to register the live socket against the subscription.

    Once registered, the service forwards any outbound bus message for that
    topic to the client as a ``SubscriptionUpdateMessage``.

    Clients may also send ``PublishMessage`` frames to push payloads onto the
    inbound bus.
    """

    def __init__(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        """Initialise the service with the shared message buses.

        Args:
            inbound_bus: Bus for publishing messages received from WebSocket clients.
            outbound_bus: Bus to subscribe to for forwarding updates to clients.
        """
        self._inbound_bus = inbound_bus
        self._outbound_bus = outbound_bus

        self._topic_subscriptions_dict: dict[TopicPath, list[UUID]] = {}
        self._subscription_websocket_dict: dict[UUID, WebSocket] = {}

        self._active_tasks: set[asyncio.Task] = set()
        self._running = False

    async def start(self) -> None:
        """Start the service and subscribe to the outbound bus for updates."""
        self._running = True
        self._outbound_bus.subscribe(self._handle_incoming_update)

    async def stop(self) -> None:
        """Stop the service, cancel all active connection tasks, and clean up."""
        self._running = False
        for task in self._active_tasks:
            task.cancel()
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
        self._active_tasks.clear()

    async def add(self, websocket: WebSocket) -> None:
        """Accept and serve a WebSocket connection until it closes or errors.

        Accepts the connection, registers the current task for lifecycle
        management, then enters a receive loop. Each received JSON frame is
        dispatched based on its type:

        - ``SubscriptionMessage``: associates the WebSocket with the
          pre-created subscription ID so future updates can be pushed to it.
        - ``PublishMessage``: forwards the payload onto the inbound bus.

        The loop exits on disconnect, validation error, or any unexpected
        exception, closing the socket with an appropriate status code.

        Args:
            websocket: The incoming WebSocket connection to accept and serve.
        """
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
        """Create a new subscription for the given topic and return its ID.

        The returned UUID must be sent by the client in a ``SubscriptionMessage``
        after opening a WebSocket to bind the live connection to this subscription.

        Args:
            topic: The topic path the client wishes to subscribe to.

        Returns:
            A freshly generated UUID identifying the new subscription.
        """
        subscription_id = uuid4()

        if topic not in self._topic_subscriptions_dict:
            self._topic_subscriptions_dict[topic] = []
        self._topic_subscriptions_dict[topic].append(subscription_id)

        return subscription_id

    def delete_subscription(self, subscription_id: UUID) -> None:
        """Remove a subscription and its WebSocket mapping.

        If the subscription was the last one for its topic, the topic entry is
        also removed from the registry.

        Args:
            subscription_id: The ID of the subscription to delete.
        """
        self._subscription_websocket_dict.pop(subscription_id, None)
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                subscription_ids.remove(subscription_id)
                if not subscription_ids:
                    del self._topic_subscriptions_dict[topic]
                break

    def get_topic_from_subscription(self, subscription_id: UUID) -> TopicPath | None:
        """Look up the topic path associated with a subscription ID.

        Args:
            subscription_id: The subscription ID to resolve.

        Returns:
            The ``TopicPath`` the subscription was created for, or ``None`` if
            the subscription ID is not found.
        """
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                return topic
        return None

    async def _handle_incoming_update(
        self, topic: TopicPath, payload: TopicPayload
    ) -> None:
        """Forward an outbound bus update to all WebSocket clients subscribed to the topic.

        Skips topics that have no registered subscriptions. Sends a
        ``SubscriptionUpdateMessage`` to each WebSocket that has been bound to a
        matching subscription. Delivery failures are silently swallowed via
        ``return_exceptions=True``.

        Args:
            topic: The topic path of the incoming update.
            payload: The payload to forward to subscribed clients.
        """
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
