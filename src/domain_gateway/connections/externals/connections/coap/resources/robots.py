import logging

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

logger = logging.getLogger(__name__)

CONTENT_FORMAT = 50  # application/json

_ROBOT_ROUTES: dict[str, tuple[str, type[TopicPayload]]] = {
    "position": (POSITION_TOPIC_PATH, RobotPosition),
    "neighbors": (NEIGHBORS_TOPIC_PATH, RobotNeighbors),
    "movement": (MOVEMENT_TOPIC_PATH, RobotMovement),
    "sensing": (SENSING_TOPIC_PATH, RobotSensing),
}


class RobotsSubsite(resource.ObservableResource, resource.PathCapable):
    def __init__(self, cache: Cache, inbound_bus: Bus, outbound_bus: Bus) -> None:
        super().__init__()
        self._cache = cache
        self._inbound_bus = inbound_bus
        self._topic_observations: dict[str, set] = {}
        outbound_bus.subscribe(self._on_outbound_message)

    # ------------------------------------------------------------------
    # Observable support
    # ------------------------------------------------------------------

    async def add_observation(
        self, request: aiocoap.Message, serverobservation
    ) -> None:
        topic = self._topic_from_path(request.opt.uri_path)
        if topic is None:
            return

        observers = self._topic_observations.setdefault(topic, set())
        observers.add(serverobservation)

        def _cancel(self=self, obs=serverobservation, t=topic) -> None:
            self._topic_observations.get(t, set()).discard(obs)

        serverobservation.accept(_cancel)

    async def _on_outbound_message(self, topic: str, payload: TopicPayload) -> None:
        observers = self._topic_observations.get(topic)
        if not observers:
            return
        for obs in set(observers):
            obs.trigger()

    # ------------------------------------------------------------------
    # Request rendering
    # ------------------------------------------------------------------

    async def render(self, request: aiocoap.Message) -> aiocoap.Message:
        path = request.opt.uri_path
        topic, payload_class = self._resolve_route(path)

        if topic is None:
            return aiocoap.Message(code=aiocoap.NOT_FOUND)

        match request.code:
            case aiocoap.GET:
                return await self._handle_get(topic)
            case aiocoap.PUT:
                return await self._handle_put(topic, payload_class, request)
            case _:
                return aiocoap.Message(code=aiocoap.METHOD_NOT_ALLOWED)

    async def _handle_get(self, topic: str) -> aiocoap.Message:
        payload = await self._cache.get(topic)
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

    # ------------------------------------------------------------------
    # Routing helpers
    # ------------------------------------------------------------------

    def _resolve_route(
        self, path: tuple[str, ...]
    ) -> tuple[str, type[TopicPayload]] | tuple[None, None]:
        """Resolve a path to (topic, payload_class), or (None, None) if invalid."""
        if len(path) != 2:
            return None, None
        raw_id, endpoint = path
        try:
            robot_id = int(raw_id)
        except ValueError:
            return None, None
        route = _ROBOT_ROUTES.get(endpoint)
        if route is None:
            return None, None
        topic_template, payload_class = route
        return topic_template.format(robot_id=robot_id), payload_class

    def _topic_from_path(self, path: tuple[str, ...]) -> str | None:
        """Return only the resolved topic string, or None if invalid."""
        topic, _ = self._resolve_route(path)
        return topic
