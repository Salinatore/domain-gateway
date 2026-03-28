from abc import ABC

from domain_gateway.models.connections.mqtt import TopicPath
from domain_gateway.models.mqtt_topics import TopicPayload


class Handler(ABC):
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        pass
