from domain_gateway.core.connection import Connection
from domain_gateway.models.topic.paths import TopicPath
from domain_gateway.models.topic.payloads import TopicPayload


class MockMQTTConnection(Connection):
    """
    Bypasses real MQTT. On start(), subscribes to inbound bus and
    echoes every message directly onto the outbound bus.
    """

    async def start(self) -> None:
        self._inbound_bus.subscribe(self._echo)

    async def stop(self) -> None:
        pass

    async def _echo(self, topic: TopicPath, payload: TopicPayload) -> None:
        await self._outbound_bus.publish(topic, payload)
