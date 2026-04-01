from uuid import UUID

from pydantic import BaseModel

from domain_gateway.models.topic.paths import TopicPath

type SubscriptionID = UUID

# ── Request bodies ─────────────────────────────────────────────────────────────


class SubscriptionCreate(BaseModel):
    topic_of_interest: TopicPath


# ── Response ───────────────────────────────────────────────────────────────────


class SubscriptionData(BaseModel):
    id: SubscriptionID
    subscribed_to_topic: TopicPath


class SubscriptionCreateResponse(BaseModel):
    id: SubscriptionID
    subscribed_to_topic: TopicPath
