import asyncio
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
from domain_gateway.core.cache import cache as shared_cache
from domain_gateway.core.handler import Handler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

logger = logging.getLogger(__name__)

COAP_BIND_HOST = "localhost"
COAP_BIND_PORT = 5683


class CoAPHandler(Handler):
    def __init__(self, cache: Cache = shared_cache) -> None:
        self._cache = cache
        self._inbound_bus: Bus | None = None
        self._server_task: asyncio.Task | None = None
        self._context: aiocoap.Context | None = None

    @override
    async def start(self, inbound_bus: Bus, outbound_bus: Bus) -> None:
        self._inbound_bus = inbound_bus
        self._server_task = asyncio.create_task(self._serve(), name="coap-server")

    @override
    async def stop(self) -> None:
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
            self._server_task = None

        if self._context:
            await self._context.shutdown()
            self._context = None

    @override
    async def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        pass  # observer notify hook

    async def _serve(self) -> None:
        assert self._inbound_bus is not None, "start() must be called before _serve()"

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

        self._context = await aiocoap.Context.create_server_context(
            site, bind=(COAP_BIND_HOST, COAP_BIND_PORT)
        )
        logger.info("CoAP server listening on coap://0.0.0.0:%d", COAP_BIND_PORT)

        try:
            await asyncio.Future()
        finally:
            await self._context.shutdown()
            self._context = None
