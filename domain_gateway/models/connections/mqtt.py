import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator

from domain_gateway.models.mqtt_topics import (
    Formation,
    Leader,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
)

TOPIC_PATTERN = re.compile(
    r"^/(robots/(\d+|\+)/(position|neighbor|movement|sensing)|computing/inputs/(formations|leader))$"
)


def validate_topic(v: str) -> str:
    if not TOPIC_PATTERN.match(v):
        raise ValueError(f"Invalid topic path: {v!r}")
    return v


TopicPath = Annotated[str, AfterValidator(validate_topic)]


# ── robots ───────────────────────────────────────────────────────────────────


class BaseResponse(BaseModel):
    forwarded_at: datetime


class PositionResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: RobotPosition


class MovementResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: RobotMovement


class NeighborsResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: RobotNeighbors


class SensingResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: RobotSensing


# ── inputs ───────────────────────────────────────────────────────────────────


class FormationResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: Formation


class LeaderResponse(BaseResponse):
    forwarded_to_topic: TopicPath
    forwarded_item: Leader
