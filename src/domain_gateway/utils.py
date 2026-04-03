from fastapi import APIRouter

from domain_gateway.core.connection import Connection


def include_routers(root_router: APIRouter, connections: list[Connection]) -> None:
    """
    Utility function to include multiple routers in a root router.
    """
    for handler in connections:
        if r := handler.router:
            root_router.include_router(r)
