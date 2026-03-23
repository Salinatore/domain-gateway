from fastapi import APIRouter, HTTPException, status

subscriptions_router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
)


@subscriptions_router.get("/{subscription_id}")
async def read_subscription(subscription_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.post("")
async def create_subscription():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.delete("/{subscription_id}")
async def delete_subscription(subscription_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.put("/{subscription_id}")
async def update_subscription(subscription_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@subscriptions_router.patch("/{subscription_id}")
async def partial_update_subscription(subscription_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
