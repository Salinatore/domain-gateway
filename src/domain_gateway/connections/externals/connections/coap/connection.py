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
from domain_gateway.core.monitor import HealthHandle, Status
from domain_gateway.settings import settings

logger = logging.getLogger(__name__)


class CoAPConnection(Connection):
    def __init__(
        self,
        health_handle: HealthHandle,
        cache: Cache,
        inbound_bus: Bus,
        outbound_bus: Bus,
    ) -> None:
        super().__init__(inbound_bus=inbound_bus, outbound_bus=outbound_bus)

        self._health_handle = health_handle
        self._cache = cache
        self._context: aiocoap.Context | None = None

    @override
    async def start(self) -> None:
        site = resource.Site()
        site.add_resource(
            ["robots"],
            RobotsSubsite(self._cache, self._inbound_bus, self._outbound_bus),
        )
        site.add_resource(
            ["computing", "inputs", "formation"],
            FormationResource(self._cache, self._inbound_bus, self._outbound_bus),
        )
        site.add_resource(
            ["computing", "inputs", "leader"],
            LeaderResource(self._cache, self._inbound_bus, self._outbound_bus),
        )

        try:
            if settings.coap_server_listen_url:
                self._context = await aiocoap.Context.create_server_context(
                    site, bind=(settings.coap_server_listen_url, None)
                )
            else:
                self._context = await aiocoap.Context.create_server_context(site)
            self._health_handle.report(Status.UP)
        except OSError as e:
            logger.error("Failed to bind CoAP server: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error starting CoAP server: %s", e)
            raise
        logger.info("CoAP server started")

    @override
    async def stop(self) -> None:
        if self._context:
            await self._context.shutdown()
            self._health_handle.report(Status.DOWN)
            self._context = None
