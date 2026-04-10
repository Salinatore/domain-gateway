import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.dependencies.container import Container, container

logging.basicConfig(level=logging.INFO)


def create_app(container: Container) -> FastAPI:
    """Create a FastAPI application using the given container."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await asyncio.gather(
            container.external_connections.start(),
            container.internal_connections.start(),
            *[service.start() for service in container.lifespan_services],
        )
        yield
        await asyncio.gather(
            container.external_connections.stop(),
            container.internal_connections.stop(),
            *[service.stop() for service in container.lifespan_services],
        )

    app = FastAPI(
        title="Domain Gateway API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(container.external_connections.router)
    app.include_router(container.internal_connections.router)

    return app


app = create_app(container)
