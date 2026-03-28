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


def make_validator(pattern: re.Pattern):
    def validate(v: str) -> str:
        if not pattern.match(v):
            raise ValueError(f"Invalid topic: {v!r}")
        return v

    return validate


TOPIC_PATTERN = re.compile(
    r"^/(robots/(\d+|\+)/(position|neighbors|movement|sensing)|computing/inputs/(formations|leader))$"
)
POSITION_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/position$")
NEIGHBORS_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/neighbors$")
MOVEMENT_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/movement$")
SENSING_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/sensing$")
FORMATION_TOPIC_PATTERN = re.compile(r"^/computing/inputs/formations$")
LEADER_TOPIC_PATTERN = re.compile(r"^/computing/inputs/leader$")


TopicPath = Annotated[str, AfterValidator(make_validator(TOPIC_PATTERN))]
PositionTopicPath = Annotated[
    str, AfterValidator(make_validator(POSITION_TOPIC_PATTERN))
]
NeighborsTopicPath = Annotated[
    str, AfterValidator(make_validator(NEIGHBORS_TOPIC_PATTERN))
]
MovementTopicPath = Annotated[
    str, AfterValidator(make_validator(MOVEMENT_TOPIC_PATTERN))
]
SensingTopicPath = Annotated[str, AfterValidator(make_validator(SENSING_TOPIC_PATTERN))]
FormationTopicPath = Annotated[
    str, AfterValidator(make_validator(FORMATION_TOPIC_PATTERN))
]
LeaderTopicPath = Annotated[str, AfterValidator(make_validator(LEADER_TOPIC_PATTERN))]


# ── robots ───────────────────────────────────────────────────────────────────


class BaseResponse(BaseModel):
    """Base response model for MQTT topic forwarding."""

    forwarded_at: datetime


class PositionResponse(BaseResponse):
    forwarded_to_topic: PositionTopicPath
    forwarded_item: RobotPosition


class MovementResponse(BaseResponse):
    forwarded_to_topic: MovementTopicPath
    forwarded_item: RobotMovement


class NeighborsResponse(BaseResponse):
    forwarded_to_topic: NeighborsTopicPath
    forwarded_item: RobotNeighbors


class SensingResponse(BaseResponse):
    forwarded_to_topic: SensingTopicPath
    forwarded_item: RobotSensing


# ── inputs ───────────────────────────────────────────────────────────────────


class FormationResponse(BaseResponse):
    forwarded_to_topic: FormationTopicPath
    forwarded_item: Formation


class LeaderResponse(BaseResponse):
    forwarded_to_topic: LeaderTopicPath
    forwarded_item: Leader
