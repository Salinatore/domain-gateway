"""
Internal message bus used to route payloads between protocol connections.

Two singleton instances are created at module level:
- ``inbound_bus``: carries messages from external clients toward the domain.
- ``outbound_bus``: carries messages from the domain back to external clients.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, override

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

logger = logging.getLogger(__name__)


class Bus(ABC):
    """Abstract publish/subscribe message bus."""

    @abstractmethod
    async def publish(self, topic: TopicPath, payload: TopicPayload) -> None:
        """Publish a payload to all current subscribers.

        Args:
            topic: The topic path the payload belongs to.
            payload: The validated topic payload to broadcast.
        """

    @abstractmethod
    def subscribe(
        self, callback: Callable[[TopicPath, TopicPayload], Awaitable[None]]
    ) -> None:
        """Register an async callback to be called on every published message.

        Args:
            callback: An async callable that receives (topic, payload).
        """


class MessageBus(Bus):
    """In‑memory publish/subscribe message bus with fire‑and‑forget delivery.

    This bus decouples message producers from consumers by dispatching each
    published message to all registered subscribers in independent background
    tasks. Publishers are never blocked by slow or failing subscribers.

    Attributes:
        _subscribers: List of async callbacks registered to receive messages.
    """

    def __init__(self) -> None:
        """Initialize an empty message bus."""
        self._subscribers: list[
            Callable[[TopicPath, TopicPayload], Awaitable[None]]
        ] = []

    @override
    async def publish(self, topic: TopicPath, payload: TopicPayload) -> None:
        """Publish a message to all current subscribers asynchronously.

        The message is delivered to each subscriber in a separate background
        task. This method returns immediately; subscriber processing happens
        concurrently and does not block the publisher.

        Args:
            topic: The topic path the payload belongs to.
            payload: The validated topic payload to broadcast.
        """
        for subscriber in self._subscribers:
            # Create an independent task for each subscriber to isolate failures
            asyncio.create_task(
                self._safe_invoke(subscriber, topic, payload),
                name=f"bus-subscriber-{topic}",
            )

    async def _safe_invoke(
        self,
        subscriber: Callable[[TopicPath, TopicPayload], Awaitable[None]],
        topic: TopicPath,
        payload: TopicPayload,
    ) -> None:
        """Invoke a subscriber and catch any exceptions to prevent task crashes.

        Args:
            subscriber: The async callback to invoke.
            topic: The topic being published.
            payload: The payload being published.
        """
        try:
            await subscriber(topic, payload)
        except Exception:
            logger.exception(
                "Subscriber %s failed while processing topic %s",
                subscriber.__name__,
                topic,
            )

    @override
    def subscribe(
        self, callback: Callable[[TopicPath, TopicPayload], Awaitable[None]]
    ) -> None:
        """Register an async callback to be invoked on every published message.

        The callback will be called once for each published message, in a
        separate background task. Order of invocation is not guaranteed.

        Args:
            callback: An async callable that receives (topic, payload).
        """
        self._subscribers.append(callback)
