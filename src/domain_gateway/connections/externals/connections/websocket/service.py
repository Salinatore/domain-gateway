import logging
from typing import Annotated, Protocol
from uuid import UUID, uuid4

from fastapi import Depends, WebSocket
from pydantic import ValidationError
from starlette import status

from domain_gateway.connections.externals.connections.websocket.models.ws import (
    PublishMessage,
    SubscriptionMessage,
    SubscriptionUpdateMessage,
    client_sent_message_adapter,
)
from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload

logger = logging.getLogger(__name__)


class WebSocketManager(Protocol):
    async def add(self, websocket: WebSocket) -> None: ...


class SubscriptionManager(Protocol):
    def create_subscription(self, topic: TopicPath) -> UUID: ...
    def delete_subscription(self, subscription_id: UUID) -> None: ...
    def get_topic_from_subscription(
        self, subscription_id: UUID
    ) -> TopicPath | None: ...


class BusAware(Protocol):
    def set_buses(self, inbound: Bus, outbound: Bus) -> None: ...


class WebSocketService:
    def __init__(self) -> None:
        self._inbound_bus: Bus | None = None

        self._topic_subscriptions_dict: dict[TopicPath, list[UUID]] = {}
        self._websocket_subscription_dict: dict[WebSocket, list[UUID]] = {}

    def set_buses(self, inbound: Bus, outbound: Bus) -> None:
        self._inbound_bus = inbound  # Store the inbound bus reference to be able to publish messages to it when needed
        outbound.subscribe(
            self._handle_incoming_update
        )  # Subscribe to the inbound bus to receive messages to send to clients

    async def add(self, websocket: WebSocket) -> None:
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()
                logger.error("Received data from websocket: %s", data)
                message = client_sent_message_adapter.validate_python(data)

                match message:
                    case SubscriptionMessage():
                        for _, id_list in self._topic_subscriptions_dict.items():
                            if message.id in id_list:
                                if websocket not in self._websocket_subscription_dict:
                                    self._websocket_subscription_dict[websocket] = []
                                self._websocket_subscription_dict[websocket].append(
                                    message.id
                                )
                    case PublishMessage():
                        if not self._inbound_bus:
                            logger.warning(
                                "Received publish message before service is ready: %s",
                                data,
                            )
                            continue
                        await self._inbound_bus.publish(message.topic, message.payload)
            except ValidationError as e:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                logger.error("Invalid message received from websocket: %s", e)
                break
            except Exception as e:
                await websocket.close(
                    code=status.WS_1011_INTERNAL_ERROR,
                )
                logging.error("Error while receiving data from websocket: %s", e)
                break

    def create_subscription(self, topic: TopicPath) -> UUID:
        subscription_id = uuid4()

        if topic not in self._topic_subscriptions_dict:
            self._topic_subscriptions_dict[topic] = []
        self._topic_subscriptions_dict[topic].append(subscription_id)

        return subscription_id

    def delete_subscription(self, subscription_id: UUID) -> None:
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                subscription_ids.remove(subscription_id)
                if not subscription_ids:
                    del self._topic_subscriptions_dict[topic]
                break

    def get_topic_from_subscription(self, subscription_id: UUID) -> TopicPath | None:
        for topic, subscription_ids in self._topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                return topic
        return None

    async def _handle_incoming_update(
        self, topic: TopicPath, payload: TopicPayload
    ) -> None:
        if topic not in self._topic_subscriptions_dict:
            return

        for subscription_id in self._topic_subscriptions_dict[topic]:
            for (
                websocket,
                ws_subscription_ids,
            ) in self._websocket_subscription_dict.items():
                if subscription_id in ws_subscription_ids:
                    await websocket.send_text(
                        SubscriptionUpdateMessage(
                            subscription_id=subscription_id,
                            topic=topic,
                            payload=payload,
                        ).model_dump_json()
                    )


# singleton
websocket_service = WebSocketService()


def get_websocket_manager() -> WebSocketManager:
    return websocket_service


def get_subscription_manager() -> SubscriptionManager:
    return websocket_service


def get_bus_aware() -> BusAware:
    return websocket_service


WebSocketManagerDep = Annotated[WebSocketManager, Depends(get_websocket_manager)]

SubscriptionManagerDep = Annotated[
    SubscriptionManager, Depends(get_subscription_manager)
]

BusAwareDep = Annotated[BusAware, Depends(get_bus_aware)]
