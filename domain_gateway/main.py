import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.connections.externals.handler import ExternalConnectionsHandler
from domain_gateway.connections.internals.handler import ExternalConnectionsHandler

external_connections = ExternalConnectionsHandler()
internalconnections = ExternalConnectionsHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        external_connections.start(internalconnections),
        internalconnections.start(external_connections),
    )
    yield
    await asyncio.gather(
        external_connections.stop(),
        internalconnections.stop(),
    )


app = FastAPI(
    title="Domain Gateway API",
    version="0.1.0",
    description="The Domain Gateway is responsible for routing messages between the internal components of the system and the external world that can not talk in MQTT. Here the HTTP endpoints are documented.",
    lifespan=lifespan,
)


app.include_router(external_connections.router)
app.include_router(internalconnections.router)
