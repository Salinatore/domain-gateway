from enum import StrEnum

from pydantic import BaseModel, Field


class MqttTopic(StrEnum):
    ROBOT_POSITION = "robots/{id}/position"
    ROBOT_NEIGHBORS = "robots/{id}/neighbors"
    ROBOT_MOVEMENT = "robots/{id}/movement"
    ROBOT_SENSING = "robots/{id}/sensing"
    LEADER = "leader"
    FORMATION = "formation"


class RobotPosition(BaseModel):
    robot_id: int
    x: float
    y: float
    orientation: float


class RobotMovement(BaseModel):
    left: float = Field(ge=-1.0, le=1.0)
    right: float = Field(ge=-1.0, le=1.0)


class RobotNeighbors(BaseModel):
    neighbors: list[int]


class RobotSensing(BaseModel):
    pass


class Leader(BaseModel):
    leader_id: int


class Formation(BaseModel):
    program: str

    leader: int | None = None
    collision_area: float | None = Field(None, alias="collisionArea")
    stability_threshold: float | None = Field(None, alias="stabilityThreshold")

    inter_distance_line: float | None = Field(None, alias="interDistanceLine")
    inter_distance_vertical: float | None = Field(None, alias="interDistanceVertical")

    inter_distance_v: float | None = Field(None, alias="interDistanceV")
    angle_v: float | None = Field(None, alias="angleV")

    radius: float | None = None

    inter_distance_square: float | None = Field(None, alias="interDistanceSquare")
