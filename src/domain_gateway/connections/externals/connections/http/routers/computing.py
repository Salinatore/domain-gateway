from fastapi import APIRouter, HTTPException, status

from domain_gateway.connections.externals.connections.http.models.responses import (
    FormationResponse,
    LeaderResponse,
)
from domain_gateway.dependencies.fastapi_deps import CacheDep, InboundBusDep
from domain_gateway.models.topic.paths import FORMATION_TOPIC_PATH, LEADER_TOPIC_PATH
from domain_gateway.models.topic.payloads import Formation, Leader, TopicPayload

computing_inputs_router = APIRouter(prefix="/computing/inputs", tags=["inputs"])


# ── Formation ─────────────────────────────────────────────────────────────────


@computing_inputs_router.get("/formation", response_model=Formation)
async def read_formations(cache: CacheDep) -> TopicPayload:
    formation = cache.get(FORMATION_TOPIC_PATH)
    if formation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formation not found",
        )
    return formation


@computing_inputs_router.put("/formation", response_model=FormationResponse)
async def update_formations(
    body: Formation, inbound_bus: InboundBusDep
) -> FormationResponse:
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


@computing_inputs_router.get("/leader", response_model=Leader)
async def read_leader(cache: CacheDep) -> TopicPayload:
    leader = cache.get(LEADER_TOPIC_PATH)
    if leader is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leader not found",
        )
    return leader


@computing_inputs_router.put("/leader", response_model=LeaderResponse)
async def update_leader(body: Leader, inbound_bus: InboundBusDep) -> LeaderResponse:
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
