"""
Internal message bus used to route payloads between protocol connections.

Two singleton instances are created at module level:
- ``inbound_bus``: carries messages from external clients toward the domain.
- ``outbound_bus``: carries messages from the domain back to external clients.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Annotated, Awaitable, Callable, override

from fastapi import Depends

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


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
    """In-memory fan-out message bus.

    Calls every registered subscriber concurrently via ``asyncio.gather``.
    Individual subscriber failures are swallowed so all subscribers are
    always notified.
    """

    def __init__(self) -> None:
        self._subscribers: list[
            Callable[[TopicPath, TopicPayload], Awaitable[None]]
        ] = list()

    @override
    async def publish(self, topic: TopicPath, payload: TopicPayload) -> None:
        await asyncio.gather(
            *(subscriber(topic, payload) for subscriber in self._subscribers),
            return_exceptions=True,  # Ensure all subscribers are called even if some fail
        )

    @override
    def subscribe(
        self, callback: Callable[[TopicPath, TopicPayload], Awaitable[None]]
    ) -> None:
        self._subscribers.append(callback)


# Messages coming in from external systems
inbound_bus: Bus = MessageBus()


def get_inbound_bus():
    return inbound_bus


InboundBusDep = Annotated[Bus, Depends(get_inbound_bus)]

# Messages going out to external systems
outbound_bus: Bus = MessageBus()


def get_outbound_bus():
    return outbound_bus


OutboundBusDep = Annotated[Bus, Depends(get_outbound_bus)]
