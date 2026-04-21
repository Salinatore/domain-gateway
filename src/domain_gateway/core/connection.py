from abc import ABC, abstractmethod

from domain_gateway.core.bus import Bus


class Connection(ABC):
    """Abstract base class for all protocol connections.

    Defines the lifecycle interface (start/stop) and provides access to the
    inbound and outbound message buses. Concrete subclasses implement a specific
    transport protocol (e.g. MQTT, CoAP, HTTP, WebSocket).
    """

    def __init__(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        """Initialise the connection with the shared message buses.

        Args:
            inbound_bus: Bus for publishing messages received from external clients.
            outbound_bus: Bus for receiving messages destined for external clients.
        """
        self._inbound_bus: Bus = inbound_bus
        self._outbound_bus: Bus = outbound_bus

    @abstractmethod
    async def start(self) -> None:
        """Start the connection."""

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the connection"""
