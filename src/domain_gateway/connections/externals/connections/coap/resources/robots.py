import aiocoap
import aiocoap.resource as resource
from pydantic import ValidationError

from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.models.topic.paths import (
    MOVEMENT_TOPIC_PATH,
    NEIGHBORS_TOPIC_PATH,
    POSITION_TOPIC_PATH,
    SENSING_TOPIC_PATH,
)
from domain_gateway.models.topic.payloads import (
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
    TopicPayload,
)

CONTENT_FORMAT = 50  # application/json

# Maps the last path segment to (topic_template, payload_class)
_ROBOT_ROUTES: dict[str, tuple[str, type[TopicPayload]]] = {
    "position": (POSITION_TOPIC_PATH, RobotPosition),
    "neighbors": (NEIGHBORS_TOPIC_PATH, RobotNeighbors),
    "movement": (MOVEMENT_TOPIC_PATH, RobotMovement),
    "sensing": (SENSING_TOPIC_PATH, RobotSensing),
}


class RobotsSubsite(resource.Resource, resource.PathCapable):
    """
    Registered at: site.add_resource(["robots"], RobotsSubsite(...))

    aiocoap strips the "robots" prefix before calling render(), so:
        /robots/1/position  →  uri_path = ("1", "position")
    """

    def __init__(self, cache: Cache, inbound_bus: Bus) -> None:
        super().__init__()
        self._cache = cache
        self._inbound_bus = inbound_bus

    async def render(self, request: aiocoap.Message) -> aiocoap.Message:
        path = request.opt.uri_path

        if len(path) != 2:
            return aiocoap.Message(code=aiocoap.NOT_FOUND)

        raw_id, endpoint = path

        try:
            robot_id = int(raw_id)
        except ValueError:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

        route = _ROBOT_ROUTES.get(endpoint)
        if route is None:
            return aiocoap.Message(code=aiocoap.NOT_FOUND)

        topic_template, payload_class = route
        topic = topic_template.format(robot_id=robot_id)

        match request.code:
            case aiocoap.GET:
                return self._handle_get(topic)
            case aiocoap.PUT:
                return await self._handle_put(topic, payload_class, request)
            case _:
                return aiocoap.Message(code=aiocoap.METHOD_NOT_ALLOWED)

    def _handle_get(self, topic: str) -> aiocoap.Message:
        payload = self._cache.get(topic)
        if payload is None:
            return aiocoap.Message(code=aiocoap.NOT_FOUND)
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=payload.model_dump_json().encode(),
            content_format=CONTENT_FORMAT,
        )

    async def _handle_put(
        self,
        topic: str,
        payload_class: type[TopicPayload],
        request: aiocoap.Message,
    ) -> aiocoap.Message:
        try:
            body = payload_class.model_validate_json(request.payload)
        except ValidationError:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

        await self._inbound_bus.publish(topic, body)
        return aiocoap.Message(code=aiocoap.CHANGED)
