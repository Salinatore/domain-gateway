from fastapi import APIRouter, HTTPException, status

robots_router = APIRouter(
    prefix="/robots",
    tags=["robots"],
)


@robots_router.get("/{input_id}/position")
async def read_robot_positon(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.post("/{input_id}/position")
async def update_robot_positon(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/neighborhood")
async def read_robot_neighborhood(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.post("/{input_id}/neighborhood")
async def update_robot_neighborhood(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/movements")
async def read_robot_movements(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.post("/{input_id}/movements")
async def update_robot_movements(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.get("/{input_id}/sensing")
async def read_robot_sensing(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@robots_router.post("/{input_id}/sensing")
async def update_robot_sensing(input_id: str):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
