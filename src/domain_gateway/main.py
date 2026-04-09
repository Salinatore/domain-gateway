# src/domain_gateway/main.py
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.dependencies.container import Container
from domain_gateway.dependencies.container import container as default_container

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

    description: str = """
        Bridges external clients with the internal MQTT-based domain.

        Inbound requests (HTTP, WebSocket, CoAP) are forwarded to the domain via the inbound bus.
        Domain updates flow back through the outbound bus, updating the cache and notifying WebSocket subscribers.

        > HTTP endpoints below cover REST-style reads and writes. For real-time updates, use the WebSocket (/ws) and subscription endpoints.
    """

    app = FastAPI(
        title="Domain Gateway API",
        version="0.1.0",
        description=description,
        lifespan=lifespan,
    )

    app.include_router(container.external_connections.router)
    app.include_router(container.internal_connections.router)

    # Store the container in app.state so dependencies can access it if needed
    app.state.container = container

    return app


# Production application instance (uses the global singleton container)
app = create_app(default_container)
