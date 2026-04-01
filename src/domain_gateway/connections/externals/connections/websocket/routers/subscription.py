from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from domain_gateway.connections.externals.connections.websocket.models.subscription import (
    SubscriptionCreate,
    SubscriptionCreateResponse,
    SubscriptionData,
    SubscriptionUpdate,
    SubscriptionUpdateResponse,
)

subscription_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@subscription_router.get("/{subscription_id}")
async def read_subscription(subscription_id: UUID) -> SubscriptionData:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscription_router.post("", status_code=status.HTTP_201_CREATED)
async def create_subscription(body: SubscriptionCreate) -> SubscriptionCreateResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscription_router.delete(
    "/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subscription(subscription_id: UUID) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscription_router.put("/{subscription_id}")
async def update_subscription(
    subscription_id: UUID, body: SubscriptionUpdate
) -> SubscriptionUpdateResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
