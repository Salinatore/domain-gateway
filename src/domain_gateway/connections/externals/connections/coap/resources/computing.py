import aiocoap
import aiocoap.resource as resource
from pydantic import ValidationError

from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.models.topic.paths import (
    FORMATION_TOPIC_PATH,
    LEADER_TOPIC_PATH,
)
from domain_gateway.models.topic.payloads import Formation, Leader, TopicPayload

CONTENT_FORMAT = 50  # application/json


class _BaseComputingResource(resource.Resource):
    """Shared GET/PUT logic for single-topic computing resources."""

    _topic: str
    _payload_class: type[TopicPayload]

    def __init__(self, cache: Cache, inbound_bus: Bus) -> None:
        super().__init__()
        self._cache = cache
        self._inbound_bus = inbound_bus

    async def render_get(self, request: aiocoap.Message) -> aiocoap.Message:
        payload = self._cache.get(self._topic)
        if payload is None:
            return aiocoap.Message(code=aiocoap.NOT_FOUND)
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=payload.model_dump_json().encode(),
            content_format=CONTENT_FORMAT,
        )

    async def render_put(self, request: aiocoap.Message) -> aiocoap.Message:
        try:
            body = self._payload_class.model_validate_json(request.payload)
        except ValidationError:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

        await self._inbound_bus.publish(self._topic, body)
        return aiocoap.Message(code=aiocoap.CHANGED)


class FormationResource(_BaseComputingResource):
    _topic = FORMATION_TOPIC_PATH
    _payload_class = Formation


class LeaderResource(_BaseComputingResource):
    _topic = LEADER_TOPIC_PATH
    _payload_class = Leader
