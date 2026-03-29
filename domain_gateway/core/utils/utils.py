from fastapi import APIRouter

from domain_gateway.core.interfaces.handler import Handler


def include_routers(root_router: APIRouter, handlers: list[Handler]) -> None:
    """
    Utility function to include multiple routers in a root router.
    """
    for handler in handlers:
        if r := handler.router:
            root_router.include_router(r)
