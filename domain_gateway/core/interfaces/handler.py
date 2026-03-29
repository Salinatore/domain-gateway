from abc import ABC, abstractmethod

from fastapi import APIRouter

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class MessageHandler(ABC):
    @abstractmethod
    def update(self, topic: TopicPath, payload: TopicPayload) -> None: ...


class ConnectionHandler(ABC):
    @abstractmethod
    async def start(self, message_handler: MessageHandler) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @property
    def router(self) -> APIRouter | None:
        """
        Handlers that expose HTTP/WS routes override this.
        Protocols like CoAP or MQTT return None (default).
        """
        return None


class Handler(MessageHandler, ConnectionHandler):
    pass
