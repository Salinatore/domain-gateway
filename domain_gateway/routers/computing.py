from fastapi import APIRouter, HTTPException, status

from domain_gateway.models.connections.mqtt import FormationResponse, LeaderResponse
from domain_gateway.models.mqtt_topics import Formation, Leader

computing_inputs_router = APIRouter(prefix="/computing/inputs", tags=["inputs"])


# ── Formation ─────────────────────────────────────────────────────────────────


@computing_inputs_router.get("/formation")
async def read_formations() -> Formation:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@computing_inputs_router.put("/formation")
async def update_formations(body: Formation) -> FormationResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Leader ────────────────────────────────────────────────────────────────────


@computing_inputs_router.get("/leader")
async def read_leader() -> Leader:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@computing_inputs_router.put("/leader")
async def update_leader(body: Leader) -> LeaderResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
