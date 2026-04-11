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
class TestCoAPFormation:
    PATH = "computing/inputs/formation"
    VALID_PAYLOAD = b'{"program":"circle","radius":5.0}'

    async def test_get_empty_returns_empty_content(self, coap_client, coap_port):
        """Cache empty → 2.05 Content with {} so observe registrations stay alive."""
        response = await get(coap_client, coap_url(coap_port, self.PATH))
        assert response.code == aiocoap.CONTENT
        assert json.loads(response.payload) == {}

    async def test_put_returns_changed(self, coap_client, coap_port):
        response = await put(
            coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD
        )
        assert response.code == aiocoap.CHANGED

    async def test_put_then_get(self, coap_client, coap_port):
        await put(coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD)
        response = await wait_for_payload(
            coap_client,
            coap_url(coap_port, self.PATH),
            lambda d: d.get("program") == "circle",
        )
        assert response.code == aiocoap.CONTENT
        data = json.loads(response.payload)
        assert data["program"] == "circle"
        assert data["radius"] == 5.0

    async def test_put_updates_cache(self, coap_client, coap_port):
        await put(coap_client, coap_url(coap_port, self.PATH), b'{"program":"line"}')
        await put(coap_client, coap_url(coap_port, self.PATH), b'{"program":"square"}')
        response = await wait_for_payload(
            coap_client,
            coap_url(coap_port, self.PATH),
            lambda d: d.get("program") == "square",
        )
        assert json.loads(response.payload)["program"] == "square"

    async def test_put_invalid_payload_returns_bad_request(
        self, coap_client, coap_port
    ):
        # missing required 'program' field
        response = await put(
            coap_client, coap_url(coap_port, self.PATH), b'{"radius": 5.0}'
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

        assert initial.code == aiocoap.CONTENT
        assert json.loads(initial.payload) == {}

        async def collect():
            async for msg in protocol_request.observation:
                await notification_queue.put(msg)

        collector = asyncio.create_task(collect())
        await asyncio.sleep(0)  # yield so collector enters the async for

        await put(
            coap_client,
            coap_url(coap_port, self.PATH),
            b'{"program":"star","radius":3.0}',
        )

        try:
            notification = await asyncio.wait_for(notification_queue.get(), timeout=5.0)
        finally:
            collector.cancel()
            await asyncio.gather(collector, return_exceptions=True)

        data = json.loads(notification.payload)
        assert data["program"] == "star"
        assert data["radius"] == 3.0


@pytest.mark.coap
class TestCoAPLeader:
    PATH = "computing/inputs/leader"
    VALID_PAYLOAD = b'{"leader_id":42}'

    async def test_get_empty_returns_empty_content(self, coap_client, coap_port):
        """Cache empty → 2.05 Content with {} so observe registrations stay alive."""
        response = await get(coap_client, coap_url(coap_port, self.PATH))
        assert response.code == aiocoap.CONTENT
        assert json.loads(response.payload) == {}

    async def test_put_returns_changed(self, coap_client, coap_port):
        response = await put(
            coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD
        )
        assert response.code == aiocoap.CHANGED

    async def test_put_then_get(self, coap_client, coap_port):
        await put(coap_client, coap_url(coap_port, self.PATH), self.VALID_PAYLOAD)
        response = await wait_for_payload(
            coap_client,
            coap_url(coap_port, self.PATH),
            lambda d: d.get("leader_id") == 42,
        )
        assert response.code == aiocoap.CONTENT
        assert json.loads(response.payload)["leader_id"] == 42

    async def test_put_updates_cache(self, coap_client, coap_port):
        await put(coap_client, coap_url(coap_port, self.PATH), b'{"leader_id":1}')
        await put(coap_client, coap_url(coap_port, self.PATH), b'{"leader_id":99}')
        response = await wait_for_payload(
            coap_client,
            coap_url(coap_port, self.PATH),
            lambda d: d.get("leader_id") == 99,
        )
        assert json.loads(response.payload)["leader_id"] == 99

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

        assert initial.code == aiocoap.CONTENT
        assert json.loads(initial.payload) == {}

        async def collect():
            async for msg in protocol_request.observation:
                await notification_queue.put(msg)

        collector = asyncio.create_task(collect())
        await asyncio.sleep(0)

        await put(
            coap_client,
            coap_url(coap_port, self.PATH),
            b'{"leader_id":7}',
        )

        try:
            notification = await asyncio.wait_for(notification_queue.get(), timeout=5.0)
        finally:
            collector.cancel()
            await asyncio.gather(collector, return_exceptions=True)

        assert json.loads(notification.payload)["leader_id"] == 7
