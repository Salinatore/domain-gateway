import uuid

from starlette.testclient import TestClient

# ── HTTP tests ─────────────────────────────────────────────


def test_create_subscription(test_client: TestClient):
    response = test_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert body["subscribed_to_topic"] == "/robots/1/position"


def test_read_subscription(test_client: TestClient):
    create = test_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    sub_id = create.json()["id"]

    response = test_client.get(f"/subscriptions/{sub_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sub_id


def test_read_nonexistent_subscription(test_client: TestClient):
    response = test_client.get(f"/subscriptions/{uuid.uuid4()}")
    assert response.status_code == 404


def test_delete_subscription(test_client: TestClient):
    create = test_client.post(
        "/subscriptions",
        json={"topic_of_interest": "/robots/1/position"},
    )
    sub_id = create.json()["id"]

    delete = test_client.delete(f"/subscriptions/{sub_id}")
    assert delete.status_code == 204

    get = test_client.get(f"/subscriptions/{sub_id}")
    assert get.status_code == 404


# ── WebSocket ─────────────────────────────────────────────────────────────────


def test_websocket_accepts_connection(test_client: TestClient):
    with test_client.websocket_connect("/ws"):
        pass
