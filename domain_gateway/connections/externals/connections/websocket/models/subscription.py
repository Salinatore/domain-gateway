from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain_gateway.models.topic.paths import TopicPath

type SubscriptionID = UUID

# ── Request bodies ─────────────────────────────────────────────────────────────


class SubscriptionCreate(BaseModel):
    topic_of_interest: TopicPath


class SubscriptionUpdate(SubscriptionCreate):
    pass


# ── Response ───────────────────────────────────────────────────────────────────


class SubscriptionData(BaseModel):
    id: SubscriptionID
    subscribed_to_topic: TopicPath
    created_at: datetime


class SubscriptionCreateResponse(BaseModel):
    id: SubscriptionID
    subscribed_to_topic: TopicPath
    created_at: datetime


class SubscriptionUpdateResponse(BaseModel):
    subscribed_to_topic: TopicPath
    changed_at: datetime
