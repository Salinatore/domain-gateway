import uuid

from starlette.testclient import TestClient

# ── HTTP subscription tests (existing) ─────────────────────────────────────────


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


# ── WebSocket tests ────────────────────────────────────────────────────────────


def test_websocket_accepts_connection(test_client: TestClient):
    """WebSocket endpoint should accept the connection."""
    with test_client.websocket_connect("/ws"):
        pass


def test_websocket_receives_multiple_updates(test_client):
    """Each PUT should deliver a separate message to the subscriber."""
    sub_id = test_client.post(
        "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
    ).json()["id"]

    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"id": sub_id})

        test_client.put(
            "/robots/1/position",
            json={"robot_id": 1, "x": 1.0, "y": 1.0, "orientation": 0.0},
        )
        msg1 = ws.receive_json()

        test_client.put(
            "/robots/1/position",
            json={"robot_id": 1, "x": 2.0, "y": 2.0, "orientation": 0.0},
        )
        msg2 = ws.receive_json()

    assert msg1["payload"]["x"] == 1.0
    assert msg2["payload"]["x"] == 2.0


def test_websocket_only_receives_subscribed_topic(test_client):
    """Updates to a different topic should not reach the subscriber."""
    sub_id = test_client.post(
        "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
    ).json()["id"]

    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"id": sub_id})

        test_client.put(
            "/robots/2/position",
            json={"robot_id": 2, "x": 99.0, "y": 99.0, "orientation": 0.0},
        )
        test_client.put(
            "/robots/1/position",
            json={"robot_id": 1, "x": 5.0, "y": 5.0, "orientation": 0.0},
        )
        msg = ws.receive_json()

    assert msg["payload"]["x"] == 5.0


def test_websocket_publish_via_ws_updates_cache(test_client):
    """A PublishMessage sent over WebSocket should reach the cache."""
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json(
            {
                "topic": "/robots/3/position",
                "payload": {"robot_id": 3, "x": 30.0, "y": 40.0, "orientation": 1.57},
            }
        )

    resp = test_client.get("/robots/3/position")
    assert resp.status_code == 200
    assert resp.json()["x"] == 30.0
    assert resp.json()["y"] == 40.0


def test_deleted_subscription_receives_no_updates(test_client):
    """After deleting a subscription, no further messages should be delivered."""
    sub_id = test_client.post(
        "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
    ).json()["id"]

    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"id": sub_id})
        test_client.put(
            "/robots/1/position",
            json={"robot_id": 1, "x": 1.0, "y": 1.0, "orientation": 0.0},
        )
        ws.receive_json()

    test_client.delete(f"/subscriptions/{sub_id}")

    assert test_client.get(f"/subscriptions/{sub_id}").status_code == 404
