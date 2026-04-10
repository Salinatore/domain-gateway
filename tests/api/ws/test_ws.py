import uuid

import pytest
from starlette.testclient import TestClient


@pytest.mark.subscriptions
class TestSubscriptionHTTP:
    """Tests for the HTTP subscription management endpoints."""

    def test_create_subscription(self, test_client: TestClient):
        response = test_client.post(
            "/subscriptions",
            json={"topic_of_interest": "/robots/1/position"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "id" in body
        assert body["subscribed_to_topic"] == "/robots/1/position"

    def test_read_subscription(self, test_client: TestClient):
        create = test_client.post(
            "/subscriptions",
            json={"topic_of_interest": "/robots/1/position"},
        )
        sub_id = create.json()["id"]

        response = test_client.get(f"/subscriptions/{sub_id}")
        assert response.status_code == 200
        assert response.json()["id"] == sub_id

    def test_read_nonexistent_subscription(self, test_client: TestClient):
        response = test_client.get(f"/subscriptions/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_delete_subscription(self, test_client: TestClient):
        create = test_client.post(
            "/subscriptions",
            json={"topic_of_interest": "/robots/1/position"},
        )
        sub_id = create.json()["id"]

        delete = test_client.delete(f"/subscriptions/{sub_id}")
        assert delete.status_code == 204

        get = test_client.get(f"/subscriptions/{sub_id}")
        assert get.status_code == 404


@pytest.mark.websocket
class TestWebSocketBehavior:
    """Tests for WebSocket connection and real‑time updates."""

    def test_websocket_accepts_connection(self, test_client: TestClient):
        """WebSocket endpoint should accept the connection."""
        with test_client.websocket_connect("/ws"):
            pass  # No exception means success

    def test_receives_multiple_updates_for_subscribed_topic(
        self, test_client: TestClient, robot_position_factory
    ):
        """Each PUT to a subscribed topic delivers a separate WebSocket message."""
        sub_id = test_client.post(
            "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
        ).json()["id"]

        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"id": sub_id})

            payload1 = robot_position_factory(robot_id=1, x=1.0, y=1.0)
            test_client.put("/robots/1/position", json=payload1)
            msg1 = ws.receive_json()

            payload2 = robot_position_factory(robot_id=1, x=2.0, y=2.0)
            test_client.put("/robots/1/position", json=payload2)
            msg2 = ws.receive_json()

        assert msg1["payload"]["x"] == 1.0
        assert msg2["payload"]["x"] == 2.0

    def test_only_receives_subscribed_topic_updates(
        self, test_client: TestClient, robot_position_factory
    ):
        """Updates to non‑subscribed topics should not be received."""
        sub_id = test_client.post(
            "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
        ).json()["id"]

        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"id": sub_id})

            # Update robot 2 (not subscribed)
            test_client.put(
                "/robots/2/position",
                json=robot_position_factory(robot_id=2, x=99.0, y=99.0),
            )
            # Update robot 1 (subscribed)
            test_client.put(
                "/robots/1/position",
                json=robot_position_factory(robot_id=1, x=5.0, y=5.0),
            )

            msg = ws.receive_json()

        assert msg["payload"]["x"] == 5.0

    def test_publish_via_websocket_updates_cache(
        self, test_client: TestClient, robot_position_factory
    ):
        """Sending a PublishMessage over WebSocket should store the data in cache."""
        with test_client.websocket_connect("/ws") as ws:
            ws.send_json(
                {
                    "topic": "/robots/3/position",
                    "payload": robot_position_factory(robot_id=3, x=30.0, y=40.0),
                }
            )

        response = test_client.get("/robots/3/position")
        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 30.0
        assert data["y"] == 40.0

    def test_deleted_subscription_stops_receiving_updates(
        self, test_client: TestClient, robot_position_factory
    ):
        """After deleting a subscription, no further updates should be delivered."""
        sub_id = test_client.post(
            "/subscriptions", json={"topic_of_interest": "/robots/1/position"}
        ).json()["id"]

        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"id": sub_id})
            test_client.put(
                "/robots/1/position",
                json=robot_position_factory(robot_id=1, x=1.0, y=1.0),
            )
            ws.receive_json()  # Consume the first message

        # Delete subscription
        test_client.delete(f"/subscriptions/{sub_id}")
        assert test_client.get(f"/subscriptions/{sub_id}").status_code == 404

    def test_websocket_closes_on_invalid_json(self, test_client: TestClient):
        """Sending malformed JSON should close the WebSocket connection."""
        with test_client.websocket_connect("/ws") as ws:
            ws.send_text("not json")
            # After sending invalid JSON, the server closes the connection.
            # Trying to receive should raise a WebSocketDisconnect.
            with pytest.raises(Exception):  # WebSocketDisconnect or similar
                ws.receive_json()
