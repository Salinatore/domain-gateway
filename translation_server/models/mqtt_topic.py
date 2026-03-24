from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# Topic: robots/{id}/position
# ─────────────────────────────────────────────
class RobotPosition(BaseModel):
    robot_id: int
    x: float
    y: float
    orientation: float  # radians, yaw around Z axis


# ─────────────────────────────────────────────
# Topic: robots/{id}/move
# ─────────────────────────────────────────────
class RobotMovement(BaseModel):
    left: float = Field(ge=-1.0, le=1.0)  # left  wheel speed [-1, 1]
    right: float = Field(ge=-1.0, le=1.0)  # right wheel speed [-1, 1]


# ─────────────────────────────────────────────
# Topic: robots/{id}/neighbors
# ─────────────────────────────────────────────
class RobotNeighbors(BaseModel):
    neighbors: list[int]  # list of neighbor robot IDs


class RobotSensing(BaseModel):
    pass


# ─────────────────────────────────────────────
# Topic: leader
# ─────────────────────────────────────────────
class Leader(BaseModel):
    leader_id: int


# ─────────────────────────────────────────────
# Topic: sensing
# ─────────────────────────────────────────────
class Formation(BaseModel):
    program: str  # "pointToLeader", "vShape", …

    # formation-specific parameters
    leader: int | None = None
    collision_area: float | None = Field(None, alias="collisionArea")
    stability_threshold: float | None = Field(None, alias="stabilityThreshold")

    # Line / VerticalLine
    inter_distance_line: float | None = Field(None, alias="interDistanceLine")
    inter_distance_vertical: float | None = Field(None, alias="interDistanceVertical")

    # V-formation
    inter_distance_v: float | None = Field(None, alias="interDistanceV")
    angle_v: float | None = Field(None, alias="angleV")

    # Circle
    radius: float | None = None

    # Square
    inter_distance_square: float | None = Field(None, alias="interDistanceSquare")

    model_config = {"populate_by_name": True}
