import asyncio
from abc import ABC, abstractmethod
from typing import Annotated, Awaitable, Callable, override

from fastapi import Depends

from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class Bus(ABC):
    @abstractmethod
    async def publish(self, topic: TopicPath, payload: TopicPayload) -> None: ...

    @abstractmethod
    def subscribe(
        self, callback: Callable[[TopicPath, TopicPayload], Awaitable[None]]
    ) -> None: ...


class MessageBus(Bus):
    def __init__(self) -> None:
        self._subscribers: list[
            Callable[[TopicPath, TopicPayload], Awaitable[None]]
        ] = list()

    @override
    async def publish(self, topic: TopicPath, payload: TopicPayload) -> None:
        await asyncio.gather(
            *(subscriber(topic, payload) for subscriber in self._subscribers),
            return_exceptions=True,  # Ensure all subscribers are called even if some fail
        )

    @override
    def subscribe(
        self, callback: Callable[[TopicPath, TopicPayload], Awaitable[None]]
    ) -> None:
        self._subscribers.append(callback)


# Messages coming in from external systems
inbound_bus: Bus = MessageBus()


def get_inbound_bus():
    return inbound_bus


InboundBusDep = Annotated[Bus, Depends(get_inbound_bus)]

# Messages going out to external systems
outbound_bus: Bus = MessageBus()


def get_outbound_bus():
    return outbound_bus


OutboundBusDep = Annotated[Bus, Depends(get_outbound_bus)]
