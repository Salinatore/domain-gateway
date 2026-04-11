import asyncio
import json

import aiocoap
import pytest

CONTENT_FORMAT = 50  # application/json


def coap_url(port: int, path: str) -> str:
    return f"coap://127.0.0.1:{port}/{path}"


async def get(client: aiocoap.Context, url: str) -> aiocoap.Message:
    request = aiocoap.Message(code=aiocoap.GET, uri=url)
    return await client.request(request).response


async def put(client: aiocoap.Context, url: str, payload: bytes) -> aiocoap.Message:
    request = aiocoap.Message(
        code=aiocoap.PUT,
        uri=url,
        payload=payload,
        content_format=CONTENT_FORMAT,
    )
    return await client.request(request).response


async def wait_for_payload(
    client: aiocoap.Context,
    url: str,
    predicate,
    timeout: float = 2.0,
    interval: float = 0.05,
) -> aiocoap.Message:
    """Poll until the response payload satisfies predicate or timeout expires."""
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        response = await get(client, url)
        if response.code == aiocoap.CONTENT:
            data = json.loads(response.payload)
            if predicate(data):
                return response
        if asyncio.get_event_loop().time() >= deadline:
            return response
        await asyncio.sleep(interval)


@pytest.mark.coap
@pytest.mark.robots
class TestCoAPRobotPosition:
    PATH = "robots/1/position"
    VALID_PAYLOAD = b'{"robot_id":1,"x":1.0,"y":2.0,"orientation":0.5}'

    async def test_get_empty_returns_empty_content(self, coap_client, coap_port):
        """Cache empty → 2.05 Content with {} so observe registrations stay alive."""
        response = await get(coap_client, coap_url(coap_port, self.PATH))
        assert response.code == aiocoap.CONTENT
        assert json.loads(response.payload) == {}

    async def test_get_unknown_path_returns_not_found(self, coap_client, coap_port):
        """A path that doesn't match any route still returns NOT_FOUND."""
        response = await get(coap_client, coap_url(coap_port, "robots/1/unknown"))
        assert response.code == aiocoap.NOT_FOUND

    async def test_put_returns_changed(self, coap_client, coap_port):
        response = await put(
            coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD
        )
        assert response.code == aiocoap.CHANGED

    async def test_put_then_get(self, coap_client, coap_port):
        await put(coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD)
        response = await wait_for_payload(
            coap_client, coap_url(coap_port, self.PATH), lambda d: d.get("x") == 1.0
        )
        assert response.code == aiocoap.CONTENT
        data = json.loads(response.payload)
        assert data["x"] == 1.0
        assert data["y"] == 2.0

    async def test_robots_are_isolated(self, coap_client, coap_port):
        await put(
            coap_client,
            coap_url(coap_port, "robots/1/position"),
            b'{"robot_id":1,"x":5.0,"y":0.0,"orientation":0.0}',
        )
        await put(
            coap_client,
            coap_url(coap_port, "robots/2/position"),
            b'{"robot_id":2,"x":8.0,"y":0.0,"orientation":0.0}',
        )
        r1 = await wait_for_payload(
            coap_client,
            coap_url(coap_port, "robots/1/position"),
            lambda d: d.get("x") == 5.0,
        )
        r2 = await wait_for_payload(
            coap_client,
            coap_url(coap_port, "robots/2/position"),
            lambda d: d.get("x") == 8.0,
        )
        assert json.loads(r1.payload)["x"] == 5.0
        assert json.loads(r2.payload)["x"] == 8.0

    async def test_put_invalid_payload_returns_bad_request(
        self, coap_client, coap_port
    ):
        response = await put(
            coap_client, coap_url(coap_port, self.PATH), b'{"not": "valid"}'
        )
        assert response.code == aiocoap.BAD_REQUEST

    async def test_observe_receives_notification(self, coap_client, coap_port):
        """Observer stays alive even when cache is empty on registration."""
        notification_queue: asyncio.Queue[aiocoap.Message] = asyncio.Queue()

        request = aiocoap.Message(
            code=aiocoap.GET,
            uri=coap_url(coap_port, self.PATH),
            observe=0,
        )
        protocol_request = coap_client.request(request)
        initial = await protocol_request.response

        # Server now returns 2.05 Content with {} when cache is empty,
        # so the observation is kept alive from the start.
        assert initial.code == aiocoap.CONTENT
        assert json.loads(initial.payload) == {}

        async def collect():
            async for msg in protocol_request.observation:
                await notification_queue.put(msg)

        collector = asyncio.create_task(collect())

        await put(
            coap_client,
            coap_url(coap_port, self.PATH),
            b'{"robot_id":1,"x":42.0,"y":0.0,"orientation":0.0}',
        )

        try:
            notification = await asyncio.wait_for(notification_queue.get(), timeout=5.0)
        finally:
            collector.cancel()
            await asyncio.gather(collector, return_exceptions=True)

        assert json.loads(notification.payload)["x"] == 42.0
