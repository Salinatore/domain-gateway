from pydantic import BaseModel

from domain_gateway.connections.externals.connections.websocket.models.subscription import (
    SubscriptionID,
)


class SubscriptionMessage(BaseModel):
    id: SubscriptionID
