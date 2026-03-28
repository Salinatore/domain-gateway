from abc import ABC

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Handler(ABC):
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        pass
