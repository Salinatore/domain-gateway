import pytest
from starlette.testclient import TestClient


@pytest.mark.http
class TestFormation:
    ENDPOINT = "/computing/inputs/formation"

    def test_get_initially_returns_null_or_default(self, test_client: TestClient):
        # Depending on implementation, might return 404 or 200 with null data.
        # Adjust based on actual behavior.
        response = test_client.get(self.ENDPOINT)
        # Assuming cache is empty -> 404, like robot endpoints.
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, formation_factory
    ):
        payload = formation_factory(program="star", radius=5.0)
        response = test_client.put(self.ENDPOINT, json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"]["program"] == "star"
        assert body["forwarded_item"]["radius"] == 5.0
        assert "forwarded_to_topic" in body

    def test_put_then_get(self, test_client: TestClient, formation_factory):
        payload = formation_factory(program="line", interDistanceLine=10.0)
        test_client.put(self.ENDPOINT, json=payload)
        response = test_client.get(self.ENDPOINT)
        assert response.status_code == 200
        assert response.json()["program"] == "line"

    def test_put_updates_cache(self, test_client: TestClient, formation_factory):
        first = formation_factory(program="circle")
        second = formation_factory(program="square")
        test_client.put(self.ENDPOINT, json=first)
        test_client.put(self.ENDPOINT, json=second)
        response = test_client.get(self.ENDPOINT)
        assert response.json()["program"] == "square"

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {},
            {"radius": 5.0},  # missing required 'program'
            {"program": 123},  # wrong type
        ],
    )
    def test_put_invalid_payload_returns_422(
        self, test_client: TestClient, invalid_payload
    ):
        response = test_client.put(self.ENDPOINT, json=invalid_payload)
        assert response.status_code == 422


@pytest.mark.http
class TestLeader:
    ENDPOINT = "/computing/inputs/leader"

    def test_get_initially_returns_not_found(self, test_client: TestClient):
        response = test_client.get(self.ENDPOINT)
        assert response.status_code == 404

    def test_put_valid_returns_forwarded_item(
        self, test_client: TestClient, leader_factory
    ):
        payload = leader_factory(leader_id=42)
        response = test_client.put(self.ENDPOINT, json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["forwarded_item"]["leader_id"] == 42
        assert "forwarded_to_topic" in body

    def test_put_then_get(self, test_client: TestClient, leader_factory):
        payload = leader_factory(leader_id=7)
        test_client.put(self.ENDPOINT, json=payload)
        response = test_client.get(self.ENDPOINT)
        assert response.status_code == 200
        assert response.json()["leader_id"] == 7

    def test_put_updates_cache(self, test_client: TestClient, leader_factory):
        test_client.put(self.ENDPOINT, json={"leader_id": 1})
        test_client.put(self.ENDPOINT, json={"leader_id": 99})
        response = test_client.get(self.ENDPOINT)
        assert response.json()["leader_id"] == 99

    @pytest.mark.parametrize(
        "invalid_payload",
        [
            {},
            {"leader_id": "not_an_int"},
            {"wrong_key": 1},
        ],
    )
    def test_put_invalid_payload_returns_422(
        self, test_client: TestClient, invalid_payload
    ):
        response = test_client.put(self.ENDPOINT, json=invalid_payload)
        assert response.status_code == 422
