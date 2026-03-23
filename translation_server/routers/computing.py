from fastapi import APIRouter, HTTPException, status

computing_inputs_router = APIRouter(
    prefix="/computing/inputs",
    tags=["inputs"],
)


@computing_inputs_router.get("/formations")
async def read_formations():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@computing_inputs_router.post("/formations")
async def update_formations():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@computing_inputs_router.get("/leader")
async def read_leader():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@computing_inputs_router.post("/leader")
async def update_leader():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
