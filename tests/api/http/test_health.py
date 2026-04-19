import pytest
from starlette.testclient import TestClient


@pytest.mark.http
class TestHealthCheck:
    """All routes should return 503 when a critical connection is DOWN."""

    ENDPOINTS = [
        ("GET", "/robots/1/position"),
        ("PUT", "/robots/1/position"),
        ("GET", "/computing/inputs/formation"),
        ("PUT", "/computing/inputs/formation"),
        ("GET", "/computing/inputs/leader"),
        ("PUT", "/computing/inputs/leader"),
    ]

    @pytest.mark.parametrize("method,endpoint", ENDPOINTS)
    def test_returns_503_when_unhealthy(
        self, unhealthy_client: TestClient, method: str, endpoint: str
    ):
        response = unhealthy_client.request(method, endpoint)
        assert response.status_code == 503

    def test_503_body_contains_connection_status(self, unhealthy_client: TestClient):
        response = unhealthy_client.get("/robots/1/position")
        body = response.json()
        assert "detail" in body
        # Each entry should have status and critical fields
        for _name, info in body["detail"].items():
            assert "status" in info
            assert "critical" in info

    def test_503_critical_connection_is_down(self, unhealthy_client: TestClient):
        response = unhealthy_client.get("/robots/1/position")
        detail = response.json()["detail"]
        critical_connections = {
            name: info for name, info in detail.items() if info["critical"]
        }
        assert any(
            info["status"] == "DOWN" for info in critical_connections.values()
        ), "Expected at least one critical connection to be DOWN"
