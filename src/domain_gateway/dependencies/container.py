from typing import Protocol

from domain_gateway.connections.externals.connection import ExternalConnections
from domain_gateway.connections.externals.connections.coap.connection import (
    CoAPConnection,
)
from domain_gateway.connections.externals.connections.http.connection import (
    HTTPConnection,
)
from domain_gateway.connections.externals.connections.websocket.connection import (
    WebsocketConnection,
)
from domain_gateway.connections.internals.connection import InternalConnections
from domain_gateway.connections.internals.connections.mqtt.connection import (
    MQTTConnection,
)
from domain_gateway.core.bus import Bus, MessageBus
from domain_gateway.core.cache import Cache, MemoryCache


class LifespanService(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...


class Container:
    def __init__(self) -> None:
        # Cross-project services
        self._inbound_bus: Bus = MessageBus()
        self._outbound_bus: Bus = MessageBus()
        self._cache: Cache = MemoryCache(outbound_bus=self._outbound_bus)

        # Lifespan services
        self._lifespan_services: list[
            LifespanService
        ] = []  # TODO: cache should be a lifespan service

        # Groups
        self._internal_connections = InternalConnections(
            connections=[
                MQTTConnection(self._inbound_bus, self._outbound_bus),
            ],
            inbound_bus=self._inbound_bus,
            outbound_bus=self._outbound_bus,
        )
        self._external_connections = ExternalConnections(
            connections=[
                HTTPConnection(self._cache, self._inbound_bus, self._outbound_bus),
                WebsocketConnection(self._inbound_bus, self._outbound_bus),
                CoAPConnection(
                    cache=self._cache,
                    inbound_bus=self._inbound_bus,
                    outbound_bus=self._outbound_bus,
                ),
            ],
            inbound_bus=self._inbound_bus,
            outbound_bus=self._outbound_bus,
        )

    @property
    def lifespan_services(self) -> list[LifespanService]:
        return self._lifespan_services

    @property
    def internal_connections(self) -> InternalConnections:
        return self._internal_connections

    @property
    def external_connections(self) -> ExternalConnections:
        return self._external_connections


container = Container()
