from datetime import datetime

from pydantic import BaseModel

from domain_gateway.models.topic.paths import (
    FormationTopicPath,
    LeaderTopicPath,
    MovementTopicPath,
    NeighborsTopicPath,
    PositionTopicPath,
    SensingTopicPath,
)
from domain_gateway.models.topic.payloads import (
    Formation,
    Leader,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
)

# ── robots ───────────────────────────────────────────────────────────────────


class BaseResponse(BaseModel):
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
