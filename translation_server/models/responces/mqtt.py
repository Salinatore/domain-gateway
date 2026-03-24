from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from translation_server.models.mqtt_topics import (
    Formation,
    Leader,
    MqttTopic,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
)

# ── robots ───────────────────────────────────────────────────────────────────


class BaseResponse(BaseModel):
    forwarded_at: datetime


class PositionResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.ROBOT_POSITION] = MqttTopic.ROBOT_POSITION
    forwarded_item: RobotPosition


class MovementResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.ROBOT_MOVEMENT] = MqttTopic.ROBOT_MOVEMENT
    forwarded_item: RobotMovement


class NeighborsResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.ROBOT_NEIGHBORS] = MqttTopic.ROBOT_NEIGHBORS
    forwarded_item: RobotNeighbors


class SensingResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.ROBOT_SENSING] = MqttTopic.ROBOT_SENSING
    forwarded_item: RobotSensing


# ── inputs ───────────────────────────────────────────────────────────────────


class FormationResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.FORMATION] = MqttTopic.FORMATION
    forwarded_item: Formation


class LeaderResponse(BaseResponse):
    forwarded_to_topic: Literal[MqttTopic.LEADER] = MqttTopic.LEADER
    forwarded_item: Leader
