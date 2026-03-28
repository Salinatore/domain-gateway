from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain_gateway.egress.handler import EgressHandler

egress = EgressHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Domain Gateway API",
    version="0.1.0",
    description="API for the Domain Gateway HTTP interface.",
    lifespan=lifespan,
)

app.include_router(egress.router)
