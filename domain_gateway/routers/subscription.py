from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from domain_gateway.models.connections.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
)

subscriptions_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@subscriptions_router.get("/{subscription_id}")
async def read_subscription(subscription_id: UUID) -> SubscriptionResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.post("", status_code=status.HTTP_201_CREATED)
async def create_subscription(body: SubscriptionCreate) -> SubscriptionResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.delete(
    "/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subscription(subscription_id: UUID) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.put("/{subscription_id}")
async def update_subscription(
    subscription_id: UUID, body: SubscriptionUpdate
) -> SubscriptionResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
