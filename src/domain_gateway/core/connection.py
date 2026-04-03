from abc import ABC, abstractmethod

from fastapi import APIRouter

from domain_gateway.core.bus import Bus


class Connection(ABC):
    @abstractmethod
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @property
    def router(self) -> APIRouter | None:
        """
        Connections that expose HTTP/WS routes override this.
        Protocols like CoAP or MQTT return None (default).
        """
        return None
