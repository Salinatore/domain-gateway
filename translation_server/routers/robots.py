from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing_extensions import Literal

from translation_server.models.mqtt_topic import (
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
)

robots_router = APIRouter(
    prefix="/robots",
    tags=["robots"],
)


class PublishSuccessfull(BaseModel):
    success: Literal[True]


@robots_router.get("/{input_id}/position")
async def read_robot_positon(input_id: str) -> RobotPosition:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{input_id}/position")
async def update_robot_positon(input_id: str) -> PublishSuccessfull:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/neighborhood")
async def read_robot_neighborhood(input_id: str) -> RobotNeighbors:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{input_id}/neighborhood")
async def update_robot_neighborhood(input_id: str) -> PublishSuccessfull:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/movements")
async def read_robot_movements(input_id: str) -> RobotMovement:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{input_id}/movements")
async def update_robot_movements(input_id: str) -> PublishSuccessfull:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/sensing")
async def read_robot_sensing(input_id: str) -> RobotSensing:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.put("/{input_id}/sensing")
async def update_robot_sensing(input_id: str) -> PublishSuccessfull:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
