from fastapi import APIRouter

from domain_gateway.core.connection import Connection


def include_routers(root_router: APIRouter, connections: list[Connection]) -> None:
    """Include the router of each connection into *root_router*.

    Connections that return ``None`` from their ``router`` property are
    silently skipped (e.g. CoAP, MQTT).

    Args:
        root_router: The parent ``APIRouter`` to attach child routers to.
        connections: List of ``Connection`` instances to inspect.
    """
    for handler in connections:
        if r := handler.router:
            root_router.include_router(r)
