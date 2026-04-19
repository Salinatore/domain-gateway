from typing import Protocol

from fastapi import APIRouter

from domain_gateway.connections.externals.connection import ExternalConnections
from domain_gateway.connections.internals.connection import InternalConnections
from domain_gateway.core.bus import Bus, MessageBus
from domain_gateway.core.cache import Cache, InMemoryCache
from domain_gateway.core.monitor import HealthMonitor


class LifespanService(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...


class Container:
    def __init__(self) -> None:
        # Cross-project services
        self._inbound_bus: Bus = MessageBus()
        self._outbound_bus: Bus = MessageBus()
        self._cache: Cache = InMemoryCache(outbound_bus=self._outbound_bus)

        # Lifespan services, all of which will be started and stopped by the application lifespan like connections
        self._lifespan_services: list[LifespanService] = [self._cache]

        # Router Api for FastAPI connections that need to expose http or websocket endpoints.
        self._root_router = APIRouter()

        # Health monitor for tracking the health of connections and other services, and exposing a unified health endpoint.
        self._health_monitor = HealthMonitor()

        # Groups
        self._internal_connections = InternalConnections(
            health_monitor=self._health_monitor,
            inbound_bus=self._inbound_bus,
            outbound_bus=self._outbound_bus,
        )
        self._external_connections = ExternalConnections(
            health_monitor=self._health_monitor,
            root_router=self._root_router,
            cache=self._cache,
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

    @property
    def root_router(self) -> APIRouter:
        return self._root_router
