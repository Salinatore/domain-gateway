from abc import ABC, abstractmethod

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Cache(ABC):
    @abstractmethod
    def get(self, topic: TopicPath) -> TopicPayload | None: ...

    @abstractmethod
    def set(self, topic: TopicPath, payload: TopicPayload) -> None: ...


def cache_factory() -> Cache:
    raise NotImplementedError("Cache factory not implemented")
