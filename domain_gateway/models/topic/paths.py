import re
from typing import Annotated

from pydantic.functional_validators import AfterValidator


def make_validator(pattern: re.Pattern):
    def validate(v: str) -> str:
        if not pattern.match(v):
            raise ValueError(f"Invalid topic: {v!r}")
        return v

    return validate


TOPIC_PATTERN = re.compile(
    r"^/(robots/(\d+|\+)/(position|neighbors|movement|sensing)|computing/inputs/(formations|leader))$"
)
POSITION_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/position$")
NEIGHBORS_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/neighbors$")
MOVEMENT_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/movement$")
SENSING_TOPIC_PATTERN = re.compile(r"^/robots/(\d+|\+)/sensing$")
FORMATION_TOPIC_PATTERN = re.compile(r"^/computing/inputs/formations$")
LEADER_TOPIC_PATTERN = re.compile(r"^/computing/inputs/leader$")


TopicPath = Annotated[str, AfterValidator(make_validator(TOPIC_PATTERN))]
PositionTopicPath = Annotated[
    str, AfterValidator(make_validator(POSITION_TOPIC_PATTERN))
]
NeighborsTopicPath = Annotated[
    str, AfterValidator(make_validator(NEIGHBORS_TOPIC_PATTERN))
]
MovementTopicPath = Annotated[
    str, AfterValidator(make_validator(MOVEMENT_TOPIC_PATTERN))
]
SensingTopicPath = Annotated[str, AfterValidator(make_validator(SENSING_TOPIC_PATTERN))]
FormationTopicPath = Annotated[
    str, AfterValidator(make_validator(FORMATION_TOPIC_PATTERN))
]
LeaderTopicPath = Annotated[str, AfterValidator(make_validator(LEADER_TOPIC_PATTERN))]
