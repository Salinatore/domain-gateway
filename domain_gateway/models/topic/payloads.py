from pydantic import BaseModel, Field

type RobotID = int


class RobotPosition(BaseModel):
    robot_id: RobotID
    x: float
    y: float
    orientation: float


class RobotMovement(BaseModel):
    left: float = Field(ge=-1.0, le=1.0)
    right: float = Field(ge=-1.0, le=1.0)


class RobotNeighbors(BaseModel):
    neighbors: list[RobotID]


class RobotSensing(BaseModel):
    pass


class Leader(BaseModel):
    leader_id: RobotID


class Formation(BaseModel):
    program: str

    collision_area: float | None = Field(None, alias="collisionArea")
    stability_threshold: float | None = Field(None, alias="stabilityThreshold")

    inter_distance_line: float | None = Field(None, alias="interDistanceLine")
    inter_distance_vertical: float | None = Field(None, alias="interDistanceVertical")

    inter_distance_v: float | None = Field(None, alias="interDistanceV")
    angle_v: float | None = Field(None, alias="angleV")

    radius: float | None = None

    inter_distance_square: float | None = Field(None, alias="interDistanceSquare")


type TopicPayload = (
    RobotPosition | RobotMovement | RobotNeighbors | RobotSensing | Leader | Formation
)
