"""
In-memory cache that stores the latest payload seen for each topic.

The cache subscribes to the outbound bus and updates itself automatically.
It must be attached to a bus (via ``attach_bus``) before any reads or writes.
"""

from abc import ABC, abstractmethod
from typing import override

from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Cache(ABC):
    def __init__(self, outbound_bus: Bus):
        """Abstract last-value cache keyed by topic path."""
        outbound_bus.subscribe(self._handle_update)

    async def start(self) -> None:
        """Start the cache."""
        pass

    async def stop(self) -> None:
        """Stop the cache."""
        pass

    @abstractmethod
    async def get(self, topic: TopicPath) -> TopicPayload | None:
        """Return the latest cached payload for *topic*, or ``None``.

        Args:
            topic: The topic path to look up.

        Returns:
            The most recently received payload, or ``None`` if the topic
            has never been seen.
        """
        ...

    @abstractmethod
    async def _set(self, topic: TopicPath, payload: TopicPayload) -> None:
        """Persist *payload* under *topic* in the backing store.

        Args:
            topic: The topic path to update.
            payload: The new payload value.
        """
        ...

    async def _handle_update(self, topic: TopicPath, payload: TopicPayload) -> None:
        await self._set(topic, payload)


class MemoryCache(Cache):
    """``Cache`` implementation backed by a plain Python dict."""

    def __init__(self, outbound_bus: Bus):
        super().__init__(outbound_bus=outbound_bus)
        self._store: dict[TopicPath, TopicPayload] = {}

    @override
    async def start(self) -> None:
        """Start the cache (no-op for in-memory implementation)."""
        pass

    @override
    async def stop(self) -> None:
        """Stop the cache (no-op for in-memory implementation)."""
        pass

    @override
    async def get(self, topic: TopicPath) -> TopicPayload | None:
        return self._store.get(topic)

    @override
    async def _set(self, topic: TopicPath, payload: TopicPayload) -> None:
        self._store[topic] = payload
