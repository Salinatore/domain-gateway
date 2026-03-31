from abc import ABC, abstractmethod

from fastapi import APIRouter

from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Handler(ABC):
    @abstractmethod
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @property
    def router(self) -> APIRouter | None:
        """
        Handlers that expose HTTP/WS routes override this.
        Protocols like CoAP or MQTT return None (default).
        """
        return None

    @abstractmethod
    async def update(self, topic: TopicPath, payload: TopicPayload) -> None: ...
