from abc import ABC, abstractmethod

from fastapi import APIRouter

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class MessageHandler(ABC):
    @abstractmethod
    def update(self, topic: TopicPath, payload: TopicPayload) -> None: ...


class BaseHandler(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @property
    def router(self) -> APIRouter | None:
        """
        Handlers that expose HTTP/WS routes override this.
        Protocols like CoAP or MQTT return None (default).
        """
        return None
