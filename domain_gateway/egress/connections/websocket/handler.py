from typing import override

from fastapi import APIRouter

from domain_gateway.core.interfaces.handler import BaseHandler, MessageHandler
from domain_gateway.egress.connections.websocket.routers.subscription import (
    subscription_router,
)
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class WebsocketHandler(BaseHandler, MessageHandler):
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
        raise NotImplementedError("To be implemented.")
