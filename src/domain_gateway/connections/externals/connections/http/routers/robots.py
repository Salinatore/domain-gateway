from fastapi import APIRouter, HTTPException, status

from domain_gateway.connections.externals.connections.http.models.responses import (
    MovementResponse,
    NeighborsResponse,
    PositionResponse,
    SensingResponse,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.models.topic.paths import (
    MOVEMENT_TOPIC_PATH,
    NEIGHBORS_TOPIC_PATH,
    POSITION_TOPIC_PATH,
    SENSING_TOPIC_PATH,
)
from domain_gateway.models.topic.payloads import (
    RobotID,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
    TopicPayload,
)


class RobotRouter:
    def __init__(self, cache: Cache, inbound_bus: Bus):
        self._robots_router = APIRouter(
            prefix="/robots",
            tags=["robots"],
        )

        # ── Position ──────────────────────────────────────────────────────────────────

        @self._robots_router.get("/{robot_id}/position", response_model=RobotPosition)
        async def read_robot_position(robot_id: RobotID) -> TopicPayload:
            position = cache.get(POSITION_TOPIC_PATH.format(robot_id=robot_id))
            if position is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Position for robot {robot_id} not found",
                )
            return position

        @self._robots_router.put("/{robot_id}/position")
        async def update_robot_position(
            robot_id: RobotID, body: RobotPosition
        ) -> PositionResponse:
            try:
                await inbound_bus.publish(
                    POSITION_TOPIC_PATH.format(robot_id=robot_id), body
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish position update: {e}",
                ) from e
            return PositionResponse(
                forwarded_to_topic=POSITION_TOPIC_PATH.format(robot_id=robot_id),
                forwarded_item=body,
            )

        # ── Neighborhood ──────────────────────────────────────────────────────────────

        @self._robots_router.get("/{robot_id}/neighbors", response_model=RobotNeighbors)
        async def read_robot_neighborhood(robot_id: RobotID) -> TopicPayload:
            neighbors = cache.get(NEIGHBORS_TOPIC_PATH.format(robot_id=robot_id))
            if neighbors is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Neighbors for robot {robot_id} not found",
                )
            return neighbors

        @self._robots_router.put(
            "/{robot_id}/neighbors", response_model=NeighborsResponse
        )
        async def update_robot_neighborhood(
            robot_id: RobotID, body: RobotNeighbors
        ) -> NeighborsResponse:
            try:
                await inbound_bus.publish(
                    NEIGHBORS_TOPIC_PATH.format(robot_id=robot_id), body
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish neighbors update: {e}",
                ) from e
            return NeighborsResponse(
                forwarded_to_topic=NEIGHBORS_TOPIC_PATH.format(robot_id=robot_id),
                forwarded_item=body,
            )

        # ── Movement ──────────────────────────────────────────────────────────────────

        @self._robots_router.get("/{robot_id}/movement", response_model=RobotMovement)
        async def read_robot_movement(robot_id: RobotID) -> TopicPayload:
            movement = cache.get(MOVEMENT_TOPIC_PATH.format(robot_id=robot_id))
            if movement is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Movement for robot {robot_id} not found",
                )
            return movement

        @self._robots_router.put(
            "/{robot_id}/movement", response_model=MovementResponse
        )
        async def update_robot_movement(
            robot_id: RobotID, body: RobotMovement
        ) -> MovementResponse:
            try:
                await inbound_bus.publish(
                    MOVEMENT_TOPIC_PATH.format(robot_id=robot_id), body
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish movement update: {e}",
                ) from e
            return MovementResponse(
                forwarded_to_topic=MOVEMENT_TOPIC_PATH.format(robot_id=robot_id),
                forwarded_item=body,
            )

        # ── Sensing ───────────────────────────────────────────────────────────────────

        @self._robots_router.get("/{robot_id}/sensing", response_model=RobotSensing)
        async def read_robot_sensing(robot_id: RobotID) -> TopicPayload:
            sensing = cache.get(SENSING_TOPIC_PATH.format(robot_id=robot_id))
            if sensing is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sensing for robot {robot_id} not found",
                )
            return sensing

        @self._robots_router.put("/{robot_id}/sensing", response_model=SensingResponse)
        async def update_robot_sensing(
            robot_id: RobotID, body: RobotSensing
        ) -> SensingResponse:
            try:
                await inbound_bus.publish(
                    SENSING_TOPIC_PATH.format(robot_id=robot_id), body
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish sensing update: {e}",
                ) from e
            return SensingResponse(
                forwarded_to_topic=SENSING_TOPIC_PATH.format(robot_id=robot_id),
                forwarded_item=body,
            )

    @property
    def router(self) -> APIRouter:
        return self._robots_router
