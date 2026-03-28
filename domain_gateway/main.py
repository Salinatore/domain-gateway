import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.egress.handler import EgressHandler
from domain_gateway.ingress.handler import IngressHandler

egress = EgressHandler()
ingress = IngressHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        ingress.start(egress),
        egress.start(ingress),
    )
    yield
    await asyncio.gather(
        ingress.stop(),
        egress.stop(),
    )


app = FastAPI(
    title="Domain Gateway API",
    version="0.1.0",
    description="The Domain Gateway is responsible for routing messages between the internal components of the system and the external world that can not talk in MQTT. Here the HTTP endpoints are documented.",
    lifespan=lifespan,
)


app.include_router(egress.router)
app.include_router(ingress.router)
