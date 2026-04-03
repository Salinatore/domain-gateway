from abc import ABC, abstractmethod

from fastapi import APIRouter

from domain_gateway.core.bus import Bus


class Connection(ABC):
    """Base class for every protocol adapter (HTTP, WebSocket, CoAP, MQTT, …).

    Each concrete connection manages its own lifecycle and optionally exposes
    an FastAPI router.  The bus wiring is handled externally by
    ``ExternalConnections`` / ``InternalConnections`` so each connection only
    needs to know the ``Bus`` interface.
    """

    @abstractmethod
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        """Start the connection and wire it to the message buses.

        Args:
            inbound_bus: Bus for messages flowing from external clients to the domain.
            outbound_bus: Bus for messages flowing from the domain to external clients.
        """

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the connection and release all resources."""

    @property
    def router(self) -> APIRouter | None:
        """FastAPI router exposing HTTP/WebSocket routes, or ``None``.

        Connections backed by non-HTTP protocols (CoAP, MQTT) return ``None``.
        """
        return None
