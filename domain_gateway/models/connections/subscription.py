from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from domain_gateway.models.connections.mqtt import TopicPath

# ── Request bodies ─────────────────────────────────────────────────────────────


class SubscriptionCreate(BaseModel):
    topic_of_interest: TopicPath


class SubscriptionUpdate(SubscriptionCreate):
    pass


# ── Response ───────────────────────────────────────────────────────────────────


class SubscriptionData(BaseModel):
    id: UUID
    subscribed_to_topic: TopicPath
    created_at: datetime


class SubscriptionCreateResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    subscribed_to_topic: TopicPath
    created_at: datetime


class SubscriptionUpdateResponse(BaseModel):
    subscribed_to_topic: TopicPath
    changed_at: datetime
