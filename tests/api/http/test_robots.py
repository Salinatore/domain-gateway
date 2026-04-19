import pytest
from starlette.testclient import TestClient


@pytest.mark.http
class TestRobotPosition:
    ENDPOINT = "/robots/{robot_id}/position"

    def test_get_not_found(self, test_client: TestClient):
        response = test_client.get(self.ENDPOINT.format(robot_id=999))
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, robot_position_factory
    ):
        payload = robot_position_factory(robot_id=42, x=10.0, y=20.0)
        response = test_client.put(self.ENDPOINT.format(robot_id=42), json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"]["x"] == 10.0
        assert body["forwarded_item"]["y"] == 20.0
        assert body["forwarded_item"]["robot_id"] == 42
        assert "forwarded_to_topic" in body

    def test_put_then_get(self, test_client: TestClient, robot_position_factory):
        payload = robot_position_factory(robot_id=1, x=7.5, y=12.3)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=payload)
        response = test_client.get(self.ENDPOINT.format(robot_id=1))
        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 7.5
        assert data["y"] == 12.3

    def test_put_updates_cache(self, test_client: TestClient, robot_position_factory):
        first = robot_position_factory(robot_id=1, x=1.0)
        second = robot_position_factory(robot_id=1, x=99.0)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=first)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=second)
        response = test_client.get(self.ENDPOINT.format(robot_id=1))
        assert response.json()["x"] == 99.0

    def test_robots_are_isolated(self, test_client: TestClient, robot_position_factory):
        robot1 = robot_position_factory(robot_id=1, x=5.0)
        robot2 = robot_position_factory(robot_id=2, x=8.0)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=robot1)
        test_client.put(self.ENDPOINT.format(robot_id=2), json=robot2)
        assert test_client.get(self.ENDPOINT.format(robot_id=1)).json()["x"] == 5.0
        assert test_client.get(self.ENDPOINT.format(robot_id=2)).json()["x"] == 8.0

    @pytest.mark.parametrize(
        "invalid_payload,expected_status",
        [
            ({}, 422),
            ({"x": 1.0, "y": 2.0, "orientation": 0.0}, 422),  # missing robot_id
            ({"robot_id": 1, "y": 2.0, "orientation": 0.0}, 422),  # missing x
            ({"robot_id": 1, "x": "not_a_number", "y": 2.0, "orientation": 0.0}, 422),
        ],
    )
    def test_put_invalid_payload_returns_422(
        self, test_client: TestClient, invalid_payload, expected_status
    ):
        response = test_client.put(
            self.ENDPOINT.format(robot_id=1), json=invalid_payload
        )
        assert response.status_code == expected_status


@pytest.mark.http
class TestRobotNeighbors:
    ENDPOINT = "/robots/{robot_id}/neighbors"

    def test_get_not_found(self, test_client: TestClient):
        response = test_client.get(self.ENDPOINT.format(robot_id=999))
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, robot_neighbors_factory
    ):
        payload = robot_neighbors_factory(robot_id=42, neighbors=[7, 8, 9])
        response = test_client.put(self.ENDPOINT.format(robot_id=42), json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"]["neighbors"] == [7, 8, 9]
        assert "forwarded_to_topic" in body

    def test_put_then_get(self, test_client: TestClient, robot_neighbors_factory):
        payload = robot_neighbors_factory(robot_id=1, neighbors=[2, 3])
        test_client.put(self.ENDPOINT.format(robot_id=1), json=payload)
        response = test_client.get(self.ENDPOINT.format(robot_id=1))
        assert response.status_code == 200
        assert response.json()["neighbors"] == [2, 3]

    def test_robots_are_isolated(
        self, test_client: TestClient, robot_neighbors_factory
    ):
        r1 = robot_neighbors_factory(robot_id=1, neighbors=[2])
        r2 = robot_neighbors_factory(robot_id=2, neighbors=[1, 3])
        test_client.put(self.ENDPOINT.format(robot_id=1), json=r1)
        test_client.put(self.ENDPOINT.format(robot_id=2), json=r2)
        assert test_client.get(self.ENDPOINT.format(robot_id=1)).json()[
            "neighbors"
        ] == [2]
        assert test_client.get(self.ENDPOINT.format(robot_id=2)).json()[
            "neighbors"
        ] == [1, 3]

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {},  # missing required 'neighbors'
            {"neighbors": "not_a_list"},  # wrong type
            {"neighbors": [1, "two"]},  # mixed types (should be all integers)
        ],
    )
    def test_put_invalid_payload_returns_422(
        self, test_client: TestClient, invalid_payload
    ):
        response = test_client.put(
            self.ENDPOINT.format(robot_id=1), json=invalid_payload
        )
        assert response.status_code == 422


@pytest.mark.http
class TestRobotMovement:
    ENDPOINT = "/robots/{robot_id}/movement"

    def test_get_not_found(self, test_client: TestClient):
        response = test_client.get(self.ENDPOINT.format(robot_id=999))
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, robot_movement_factory
    ):
        payload = robot_movement_factory(robot_id=3, left=0.8, right=0.2)
        response = test_client.put(self.ENDPOINT.format(robot_id=3), json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"]["left"] == 0.8
        assert body["forwarded_item"]["right"] == 0.2

    def test_put_then_get(self, test_client: TestClient, robot_movement_factory):
        payload = robot_movement_factory(robot_id=1, left=0.1, right=-0.1)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=payload)
        response = test_client.get(self.ENDPOINT.format(robot_id=1))
        assert response.status_code == 200
        assert response.json()["left"] == 0.1

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {},  # missing required 'left' and 'right'
            {"left": 0.5},  # missing 'right'
            {"left": 2.0, "right": 0.5},  # left out of range [-1,1]
            {"left": -1.2, "right": 0.5},  # left out of range
            {"left": 0.5, "right": 1.5},  # right out of range
            {"left": "slow", "right": 0.5},  # wrong type
        ],
    )
    def test_put_invalid_payload_returns_422(
        self, test_client: TestClient, invalid_payload
    ):
        response = test_client.put(
            self.ENDPOINT.format(robot_id=1), json=invalid_payload
        )
        assert response.status_code == 422


@pytest.mark.http
class TestRobotSensing:
    ENDPOINT = "/robots/{robot_id}/sensing"

    def test_get_not_found(self, test_client: TestClient):
        response = test_client.get(self.ENDPOINT.format(robot_id=999))
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, robot_sensing_factory
    ):
        payload = robot_sensing_factory(robot_id=5)
        response = test_client.put(self.ENDPOINT.format(robot_id=5), json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"] == {}  # currently empty
        assert "forwarded_to_topic" in body

    def test_put_then_get(self, test_client: TestClient, robot_sensing_factory):
        payload = robot_sensing_factory(robot_id=1)
        test_client.put(self.ENDPOINT.format(robot_id=1), json=payload)
        response = test_client.get(self.ENDPOINT.format(robot_id=1))
        assert response.status_code == 200
        assert response.json() == {}  # empty sensing

    def test_robots_are_isolated(self, test_client: TestClient):
        # Even though payload is empty, cache should still separate by robot_id
        test_client.put(self.ENDPOINT.format(robot_id=1), json={"robot_id": 1})
        test_client.put(self.ENDPOINT.format(robot_id=2), json={"robot_id": 2})
        assert test_client.get(self.ENDPOINT.format(robot_id=1)).status_code == 200
        assert test_client.get(self.ENDPOINT.format(robot_id=2)).status_code == 200
        assert test_client.get(self.ENDPOINT.format(robot_id=3)).status_code == 404
