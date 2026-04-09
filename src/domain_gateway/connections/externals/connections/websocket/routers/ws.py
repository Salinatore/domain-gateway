from fastapi import APIRouter, WebSocket

from domain_gateway.dependencies.fastapi_deps import WebSocketManagerDep

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@ws_router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, websocket_manager: WebSocketManagerDep
):
    await websocket_manager.add(websocket)
