# fastapi_deps.py
from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from domain_gateway.connections.externals.connections.websocket.service import (
    SubscriptionManager,
    WebSocketManager,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache


async def get_cache(conn: HTTPConnection) -> Cache:
    return conn.app.state.container._cache


async def get_inbound_bus(conn: HTTPConnection) -> Bus:
    return conn.app.state.container._inbound_bus


async def get_outbound_bus(conn: HTTPConnection) -> Bus:
    return conn.app.state.container._outbound_bus


async def get_websocket_manager(conn: HTTPConnection) -> WebSocketManager:
    return conn.app.state.container._websocket_service


async def get_subscription_manager(conn: HTTPConnection) -> SubscriptionManager:
    return conn.app.state.container._websocket_service


CacheDep = Annotated[Cache, Depends(get_cache)]
InboundBusDep = Annotated[Bus, Depends(get_inbound_bus)]
OutboundBusDep = Annotated[Bus, Depends(get_outbound_bus)]
WebSocketManagerDep = Annotated[WebSocketManager, Depends(get_websocket_manager)]
SubscriptionManagerDep = Annotated[
    SubscriptionManager, Depends(get_subscription_manager)
]
