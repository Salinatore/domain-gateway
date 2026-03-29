from fastapi import APIRouter, HTTPException, status

from domain_gateway.models.topic.payloads import (
    RobotID,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
)
from domain_gateway.connections.externals.connections.http.models.responses import (
    MovementResponse,
    NeighborsResponse,
    PositionResponse,
    SensingResponse,
)

robots_router = APIRouter(prefix="/robots", tags=["robots"])


# ── Position ──────────────────────────────────────────────────────────────────


@robots_router.get("/{robot_id}/position")
async def read_robot_position(robot_id: RobotID) -> RobotPosition:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{robot_id}/position")
async def update_robot_position(
    robot_id: RobotID, body: RobotPosition
) -> PositionResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Neighborhood ──────────────────────────────────────────────────────────────


@robots_router.get("/{robot_id}/neighbors")
async def read_robot_neighborhood(robot_id: RobotID) -> RobotNeighbors:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{robot_id}/neighbors")
async def update_robot_neighborhood(
    robot_id: RobotID, body: RobotNeighbors
) -> NeighborsResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Movement ──────────────────────────────────────────────────────────────────


@robots_router.get("/{robot_id}/movement")
async def read_robot_movement(robot_id: RobotID) -> RobotMovement:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{robot_id}/movement")
async def update_robot_movement(
    robot_id: RobotID, body: RobotMovement
) -> MovementResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Sensing ───────────────────────────────────────────────────────────────────


@robots_router.get("/{robot_id}/sensing")
async def read_robot_sensing(robot_id: RobotID) -> RobotSensing:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{robot_id}/sensing")
async def update_robot_sensing(
    robot_id: RobotID, body: RobotSensing
) -> SensingResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
