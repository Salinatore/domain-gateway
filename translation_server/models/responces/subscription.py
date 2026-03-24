from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from translation_server.models.mqtt_topics import MqttTopic

# ── Request bodies ─────────────────────────────────────────────────────────────

type Interest = RobotTopic | InputTopic


class SubscriptionCreate(BaseModel):
    topic_of_interest: Interest


class RobotTopic(BaseModel):
    topic: (
        Literal[MqttTopic.ROBOT_POSITION]
        | Literal[MqttTopic.ROBOT_NEIGHBORS]
        | Literal[MqttTopic.ROBOT_MOVEMENT]
        | Literal[MqttTopic.ROBOT_SENSING]
    )
    robot_id: int


class InputTopic(BaseModel):
    topic: Literal[MqttTopic.LEADER] | Literal[MqttTopic.FORMATION]


class SubscriptionUpdate(SubscriptionCreate):
    pass


# ── Response ───────────────────────────────────────────────────────────────────


class SubscriptionResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    topic: MqttTopic
    robot_id: int
    created_at: datetime
