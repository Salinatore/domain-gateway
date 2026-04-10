import pytest


@pytest.fixture
def robot_position_payload():
    return lambda robot_id=1, x=1.0, y=2.0, orientation=0.5: {
        "robot_id": robot_id,
        "x": x,
        "y": y,
        "orientation": orientation,
    }


@pytest.fixture
def subscription_payload():
    return lambda topic="/robots/1/position": {"topic_of_interest": topic}
