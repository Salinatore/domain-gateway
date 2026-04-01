import re
from dataclasses import dataclass
from typing import Type

from domain_gateway.models.topic.paths import (
    FORMATION_TOPIC_PATTERN,
    LEADER_TOPIC_PATTERN,
    MOVEMENT_TOPIC_PATTERN,
    NEIGHBORS_TOPIC_PATTERN,
    POSITION_TOPIC_PATTERN,
    SENSING_TOPIC_PATTERN,
)
from domain_gateway.models.topic.payloads import (
    Formation,
    Leader,
    RobotMovement,
    RobotNeighbors,
    RobotPosition,
    RobotSensing,
    TopicPayload,
)


@dataclass
class TopicMapping:
    pattern: re.Pattern
    payload_class: Type[TopicPayload]


TOPIC_MAPPINGS: list[TopicMapping] = [
    TopicMapping(POSITION_TOPIC_PATTERN, RobotPosition),
    TopicMapping(NEIGHBORS_TOPIC_PATTERN, RobotNeighbors),
    TopicMapping(MOVEMENT_TOPIC_PATTERN, RobotMovement),
    TopicMapping(SENSING_TOPIC_PATTERN, RobotSensing),
    TopicMapping(FORMATION_TOPIC_PATTERN, Formation),
    TopicMapping(LEADER_TOPIC_PATTERN, Leader),
]


def resolve_payload_class(topic: str) -> Type[TopicPayload] | None:
    for mapping in TOPIC_MAPPINGS:
        if mapping.pattern.match(topic):
            return mapping.payload_class
    return None
