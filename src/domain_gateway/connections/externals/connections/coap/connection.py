import logging
from typing import override

import aiocoap
import aiocoap.resource as resource

from domain_gateway.connections.externals.connections.coap.resources.computing import (
    FormationResource,
    LeaderResource,
)
from domain_gateway.connections.externals.connections.coap.resources.robots import (
    RobotsSubsite,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.core.connection import Connection

logger = logging.getLogger(__name__)


class CoAPConnection(Connection):
    def __init__(self, cache: Cache, inbound_bus: Bus, outbound_bus: Bus) -> None:
        super().__init__(inbound_bus=inbound_bus, outbound_bus=outbound_bus)

        self._cache = cache
        self._context: aiocoap.Context | None = None

    @override
    async def start(self) -> None:
        await self._serve()

    @override
    async def stop(self) -> None:
        if self._context:
            await self._context.shutdown()
            self._context = None

    async def _serve(self) -> None:
        site = resource.Site()
        site.add_resource(
            ["robots"],
            RobotsSubsite(self._cache, self._inbound_bus),
        )
        site.add_resource(
            ["computing", "inputs", "formation"],
            FormationResource(self._cache, self._inbound_bus),
        )
        site.add_resource(
            ["computing", "inputs", "leader"],
            LeaderResource(self._cache, self._inbound_bus),
        )

        self._context = await aiocoap.Context.create_server_context(site)
        logger.info("CoAP server started")
