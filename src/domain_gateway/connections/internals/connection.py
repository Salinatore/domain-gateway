import asyncio
from typing import override

from domain_gateway.connections.internals.connections.mqtt.connection import (
    MQTTConnection,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.connection import Connection


class InternalConnections(Connection):
    """Composite connection that manages all internal protocol adapters."""

    def __init__(
        self,
        inbound_bus: Bus,
        outbound_bus: Bus,
    ):
        self._connections: list[Connection] = [
            MQTTConnection(inbound_bus=inbound_bus, outbound_bus=outbound_bus),
        ]

    async def start(self) -> None:
        await asyncio.gather(*(connection.start() for connection in self._connections))

    @override
    async def stop(self) -> None:
        await asyncio.gather(*(connection.stop() for connection in self._connections))
