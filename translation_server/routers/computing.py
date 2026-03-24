from fastapi import APIRouter, HTTPException, status

from translation_server.models.mqtt_topics import Formation, Leader
from translation_server.models.responces.mqtt import FormationResponse, LeaderResponse

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
