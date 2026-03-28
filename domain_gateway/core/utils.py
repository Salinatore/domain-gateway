from fastapi import APIRouter

from domain_gateway.core.interfaces.handler import BaseHandler


def include_routers(root_router: APIRouter, handlers: list[BaseHandler]) -> None:
    """
    Utility function to include multiple routers in a root router.
    """
    for handler in handlers:
        if r := handler.router:
            root_router.include_router(r)
