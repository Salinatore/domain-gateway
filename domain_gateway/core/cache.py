from abc import ABC, abstractmethod
from typing import Annotated, override

from fastapi import Depends

from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Cache(ABC):
    def __init__(self):
        """
        Base class for a cache that stores topic payloads.
        Subclasses should implement the get and _set methods.
        The super().__init__() must be called by subclasses.
        """
        self.ready = False

    def attach_bus(self, outbound_bus: Bus) -> None:
        self.ready = True
        outbound_bus.subscribe(self._handle_update)

    @abstractmethod
    def get(self, topic: TopicPath) -> TopicPayload | None:
        """
        Get the cached payload for a topic, or None if not present.
        _check_ready() should be called at the beginning of this method to ensure the cache is ready
        """
        ...

    @abstractmethod
    def _set(self, topic: TopicPath, payload: TopicPayload) -> None:
        """
        Internal method to update the cache.
        _check_ready() should be called at the beginning of this method to ensure the cache is ready.
        """
        ...

    async def _handle_update(self, topic: TopicPath, payload: TopicPayload) -> None:
        self._set(topic, payload)

    def _check_ready(self) -> None:
        if not self.ready:
            raise RuntimeError("Cache is not ready. Call attach_bus() first.")


class MemoryCache(Cache):
    def __init__(self):
        super().__init__()
        self._store: dict[TopicPath, TopicPayload] = {}

    @override
    def get(self, topic: TopicPath) -> TopicPayload | None:
        self._check_ready()
        return self._store.get(topic)

    @override
    def _set(self, topic: TopicPath, payload: TopicPayload) -> None:
        self._check_ready()
        self._store[topic] = payload


# singleton
cache: Cache = MemoryCache()


def get_cache() -> Cache:
    return cache


CacheDep = Annotated[Cache, Depends(get_cache)]
