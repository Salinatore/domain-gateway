# tests/fixtures/data.py
import pytest


@pytest.fixture
def robot_position_factory():
    """Return a function to build robot position payloads with defaults."""

    def _factory(robot_id=1, x=1.0, y=2.0, orientation=0.5):
        return {"robot_id": robot_id, "x": x, "y": y, "orientation": orientation}

    return _factory


@pytest.fixture
def robot_neighbors_factory():
    def _factory(robot_id=1, neighbors=[2, 3]):
        return {"robot_id": robot_id, "neighbors": neighbors}

    return _factory


@pytest.fixture
def robot_movement_factory():
    def _factory(robot_id=1, left=0.5, right=-0.3):
        return {"robot_id": robot_id, "left": left, "right": right}

    return _factory


@pytest.fixture
def robot_sensing_factory():
    def _factory(robot_id=1, **sensors):
        # currently empty per spec, but we keep extensible
        return {"robot_id": robot_id, **sensors}

    return _factory


@pytest.fixture
def formation_factory():
    def _factory(program="circle", **kwargs):
        payload = {"program": program}
        payload.update(kwargs)
        return payload

    return _factory


@pytest.fixture
def leader_factory():
    def _factory(leader_id=1):
        return {"leader_id": leader_id}

    return _factory
