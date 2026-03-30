from typing import override

from fastapi import APIRouter

from domain_gateway.core.handler import Handler, MessageHandler
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload
from domain_gateway.connections.externals.connections.websocket.routers.subscription import (
    subscription_router,
)


class WebsocketHandler(Handler):
    def __init__(self):
        self._router = APIRouter()
        self._router.include_router(subscription_router)

    @property
    @override
    def router(self) -> APIRouter:
        return self._router

    @override
    async def start(self, message_handler: MessageHandler) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass

    @override
    def update(self, topic: TopicPath, payload: TopicPayload) -> None:
        pass
