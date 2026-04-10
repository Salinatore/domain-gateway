from fastapi import APIRouter, WebSocket

from domain_gateway.connections.externals.connections.websocket.service import (
    WebSocketManager,
)


class WebsocketEndpointRouter:
    def __init__(self, websocket_manager: WebSocketManager):
        self._ws_router = APIRouter(prefix="/ws", tags=["websocket"])

        @self._ws_router.websocket("")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket_manager.add(websocket)

    @property
    def router(self) -> APIRouter:
        return self._ws_router
