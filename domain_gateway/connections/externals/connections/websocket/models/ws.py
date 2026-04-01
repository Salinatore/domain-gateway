from pydantic import BaseModel, TypeAdapter

from domain_gateway.connections.externals.connections.websocket.models.subscription import (
    SubscriptionID,
)
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

# ── client sent messages ───────────────────────────────────────────────────────────────────

type ClientSentMessage = SubscriptionMessage | PublishMessage

client_sent_message_adapter = TypeAdapter(ClientSentMessage)


class SubscriptionMessage(BaseModel):
    id: SubscriptionID


class PublishMessage(BaseModel):
    topic: TopicPath
    payload: TopicPayload


# ── server sent messages ───────────────────────────────────────────────────────────────────


class SubscriptionUpdateMessage(BaseModel):
    subscription_id: SubscriptionID
    topic: TopicPath
    payload: TopicPayload
