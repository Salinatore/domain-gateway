from domain_gateway.cache.base import Cache
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class MemoryCache(Cache):
    def __init__(self):
        self._store: dict[TopicPath, TopicPayload] = {}

    def get(self, topic: TopicPath) -> TopicPayload | None:
        return self._store.get(topic)

    def set(self, topic: TopicPath, payload: TopicPayload) -> None:
        self._store[topic] = payload
