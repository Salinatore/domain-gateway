from fastapi import APIRouter, HTTPException, status

from domain_gateway.connections.externals.connections.http.models.responses import (
    FormationResponse,
    LeaderResponse,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.models.topic.paths import FORMATION_TOPIC_PATH, LEADER_TOPIC_PATH
from domain_gateway.models.topic.payloads import Formation, Leader, TopicPayload


class ComputingRouter:
    def __init__(self, cache: Cache, inbound_bus: Bus):
        self._computing_inputs_router = APIRouter(
            prefix="/computing/inputs",
            tags=["inputs"],
        )

        # ── Formation ──────────────────────────────────────────────────────────────────

        @self._computing_inputs_router.get(
            "/formation",
            response_model=Formation,
            responses={
                status.HTTP_404_NOT_FOUND: {
                    "content": {
                        "application/json": {
                            "example": {"detail": "Formation not found"}
                        }
                    },
                }
            },
        )
        async def read_formations() -> TopicPayload:
            formation = await cache.get(FORMATION_TOPIC_PATH)
            if formation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Formation not found",
                )
            return formation

        @self._computing_inputs_router.put(
            "/formation", response_model=FormationResponse
        )
        async def update_formations(body: Formation) -> FormationResponse:
            try:
                await inbound_bus.publish(FORMATION_TOPIC_PATH, body)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish formation update: {e}",
                ) from e
            return FormationResponse(
                forwarded_to_topic=FORMATION_TOPIC_PATH,
                forwarded_item=body,
            )

        # ── Leader ────────────────────────────────────────────────────────────────────

        @self._computing_inputs_router.get(
            "/leader",
            response_model=Leader,
            responses={
                status.HTTP_404_NOT_FOUND: {
                    "content": {
                        "application/json": {"example": {"detail": "Leader not found"}}
                    },
                }
            },
        )
        async def read_leader() -> TopicPayload:
            leader = await cache.get(LEADER_TOPIC_PATH)
            if leader is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Leader not found",
                )
            return leader

        @self._computing_inputs_router.put("/leader", response_model=LeaderResponse)
        async def update_leader(body: Leader) -> LeaderResponse:
            try:
                await inbound_bus.publish(LEADER_TOPIC_PATH, body)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to publish leader update: {e}",
                ) from e
            return LeaderResponse(
                forwarded_to_topic=LEADER_TOPIC_PATH,
                forwarded_item=body,
            )

    @property
    def router(self) -> APIRouter:
        return self._computing_inputs_router
