from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from domain_gateway.connections.externals.connections.websocket.models.subscription import (
    SubscriptionCreate,
    SubscriptionCreateResponse,
    SubscriptionData,
)
from domain_gateway.dependencies.fastapi_deps import SubscriptionManagerDep

subscription_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@subscription_router.get(
    "/{subscription_id}", responses={404: {"description": "Subscription not found"}}
)
async def read_subscription(
    subscription_id: UUID, subscription_manager: SubscriptionManagerDep
) -> SubscriptionData:
    topic = subscription_manager.get_topic_from_subscription(subscription_id)
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found"
        )

    return SubscriptionData(id=subscription_id, subscribed_to_topic=topic)


@subscription_router.post("")
async def create_subscription(
    body: SubscriptionCreate, subscription_manager: SubscriptionManagerDep
) -> SubscriptionCreateResponse:
    subscription_id = subscription_manager.create_subscription(body.topic_of_interest)
    return SubscriptionCreateResponse(
        id=subscription_id, subscribed_to_topic=body.topic_of_interest
    )


@subscription_router.delete(
    "/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_subscription(
    subscription_id: UUID, subscription_manager: SubscriptionManagerDep
) -> None:
    subscription_manager.delete_subscription(subscription_id)
