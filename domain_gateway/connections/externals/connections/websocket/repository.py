from typing import Protocol
from uuid import UUID, uuid4

from fastapi import WebSocket

from domain_gateway.core.bus import Bus
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


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
        self._ready: bool = False

        self._inbound_bus: Bus | None = None

        self.topic_subscriptions_dict: dict[TopicPath, list[UUID]] = {}
        self.websocket_subscription_dict: dict[WebSocket, list[UUID]] = {}

    def set_buses(self, inbound: Bus, outbound: Bus) -> None:
        self.inbound_bus = inbound  # Store the inbound bus reference to be able to publish messages to it when needed
        outbound.subscribe(
            self._handle_incoming_update
        )  # Subscribe to the inbound bus to receive messages to send to clients
        self._ready = True

    async def add(self, websocket: WebSocket) -> None:
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()
                # TODO
            except Exception as e:
                print(f"Error receiving data from websocket: {e}")
                break

    def create_subscription(self, topic: TopicPath) -> UUID:
        subscription_id = uuid4()

        if topic not in self.topic_subscriptions_dict:
            self.topic_subscriptions_dict[topic] = []
        self.topic_subscriptions_dict[topic].append(subscription_id)

        return subscription_id

    def delete_subscription(self, subscription_id: UUID) -> None:
        for topic, subscription_ids in self.topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                subscription_ids.remove(subscription_id)
                if not subscription_ids:
                    del self.topic_subscriptions_dict[topic]
                break

    def get_topic_from_subscription(self, subscription_id: UUID) -> TopicPath | None:
        for topic, subscription_ids in self.topic_subscriptions_dict.items():
            if subscription_id in subscription_ids:
                return topic
        return None

    async def _handle_incoming_update(
        self, topic: TopicPath, payload: TopicPayload
    ) -> None:
        # This method will be called by the outbound bus when a new update is published.
        # It should send the update to all connected websockets that are subscribed to the topic.
        pass
