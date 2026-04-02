from starlette.testclient import TestClient

# ── HTTP: robots ──────────────────────────────────────────────────────────────


def test_get_robot_position_not_found(test_client: TestClient):
    """Cache is empty on startup — should return 404."""
    response = test_client.get("/robots/42/position")
    assert response.status_code == 404


def test_put_robot_position_returns_correct_body(test_client: TestClient):
    """PUT should return the forwarded item in the response body."""
    payload = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}

    response = test_client.put("/robots/1/position", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["forwarded_item"]["x"] == 1.0
    assert body["forwarded_item"]["y"] == 2.0
    assert body["forwarded_item"]["robot_id"] == 1
    assert "forwarded_to_topic" in body
    assert "forwarded_at" in body


def test_put_then_get_robot_position(test_client: TestClient):
    """PUT publishes to inbound bus → mock echoes to outbound → cache stores it → GET returns it."""
    payload = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}

    test_client.put("/robots/1/position", json=payload)

    response = test_client.get("/robots/1/position")
    assert response.status_code == 200
    body = response.json()
    assert body["x"] == 1.0
    assert body["y"] == 2.0
    assert body["robot_id"] == 1


def test_put_robot_position_updates_cache(test_client: TestClient):
    """A second PUT should overwrite the first in the cache."""
    first = {"robot_id": 1, "x": 1.0, "y": 2.0, "orientation": 0.5}
    second = {"robot_id": 1, "x": 99.0, "y": 99.0, "orientation": 1.0}

    test_client.put("/robots/1/position", json=first)
    test_client.put("/robots/1/position", json=second)

    response = test_client.get("/robots/1/position")
    assert response.status_code == 200
    assert response.json()["x"] == 99.0


def test_put_robot_position_invalid_payload(test_client: TestClient):
    """Missing required fields should return 422 Unprocessable Entity."""
    response = test_client.put("/robots/1/position", json={"x": 1.0})
    assert response.status_code == 422


def test_robots_are_isolated(test_client: TestClient):
    """Position stored for robot 1 should not affect robot 2."""
    payload = {"robot_id": 1, "x": 10.0, "y": 20.0, "orientation": 0.0}
    test_client.put("/robots/1/position", json=payload)

    response = test_client.get("/robots/2/position")
    assert response.status_code == 404


def test_not_implemented_endpoints(test_client: TestClient):
    """Endpoints not yet implemented should return 501."""
    for path in ["/robots/1/neighbors", "/robots/1/movement", "/robots/1/sensing"]:
        response = test_client.get(path)
        assert response.status_code == 501, f"Expected 501 for GET {path}"
