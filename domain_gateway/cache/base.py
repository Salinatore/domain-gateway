from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends

from domain_gateway.cache.backends.memory import MemoryCache
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Cache(ABC):
    @abstractmethod
    def get(self, topic: TopicPath) -> TopicPayload | None: ...

    @abstractmethod
    def set(self, topic: TopicPath, payload: TopicPayload) -> None: ...


def cache_factory() -> Cache:
    return MemoryCache()


# singleton
cache: Cache = cache_factory()


def get_cache() -> Cache:
    return cache


CacheDep = Annotated[Cache, Depends(get_cache)]
