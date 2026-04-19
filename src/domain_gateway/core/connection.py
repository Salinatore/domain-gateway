from abc import ABC, abstractmethod

from domain_gateway.core.bus import Bus


class Connection(ABC):
    def __init__(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        self._inbound_bus: Bus = inbound_bus
        self._outbound_bus: Bus = outbound_bus

    @abstractmethod
    async def start(self) -> None:
        """Start the connection."""

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shut down the connection"""
