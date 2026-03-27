from fastapi import FastAPI

from domain_gateway.routers import computing, robots, subscription

app = FastAPI(
    title="Domain Gateway API",
    version="0.1.0",
    description="API for the Domain Gateway HTTP interface.",
)

app.include_router(robots.robots_router)
app.include_router(computing.computing_inputs_router)
app.include_router(subscription.subscriptions_router)
