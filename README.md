# Domain Gateway

Protocol-agnostic gateway for bidirectional communication between external clients and the inner domain.

## Overview

The gateway bridges external protocols (HTTP, WebSocket, CoAP) with the internal MQTT-based domain. It routes messages through an internal bus and maintains a cache of the latest topic payloads.

```
External Clients
  ├── HTTP        ─┐
  ├── WebSocket   ─┼──► Inbound Bus ──► MQTT Broker
  └── CoAP        ─┘
                        MQTT Broker ──► Outbound Bus ──► Cache / WebSocket subscribers
```

## Protocols

| Protocol  | Direction       | Use case                            |
|-----------|-----------------|-------------------------------------|
| HTTP      | Inbound/Read    | REST-style reads and writes         |
| WebSocket | Inbound/Outbound| Real-time subscriptions             |
| CoAP      | Inbound/Read    | Constrained device communication    |
| MQTT      | Internal        | Domain message bus                  |

## Topics

| Topic                        | Payload          |
|------------------------------|------------------|
| `/robots/{id}/position`      | `RobotPosition`  |
| `/robots/{id}/movement`      | `RobotMovement`  |
| `/robots/{id}/neighbors`     | `RobotNeighbors` |
| `/robots/{id}/sensing`       | `RobotSensing`   |
| `/computing/inputs/formation`| `Formation`      |
| `/computing/inputs/leader`   | `Leader`         |

## Getting Started

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- A running MQTT broker (default: `localhost`)

### Run locally

```bash
uv sync
uv run fastapi dev
```

### Run with Docker

```bash
docker build -t domain-gateway .
docker run -e MQTT_BROKER_URL=localhost -p 8000:8000 domain-gateway
```

## Configuration

| Variable          | Default     | Description            |
|-------------------|-------------|------------------------|
| `MQTT_BROKER_URL` | `localhost` | MQTT broker hostname   |

## Adding a New Protocol

The architecture is built around a single `Handler` abstract class. Adding a new protocol means implementing the interface and registering the handler.

```python
external_connections = ExternalConnectionsHandler(
    connections=[HTTPHandler(), WebsocketHandler(), CoAPHandler(cache=cache), NewProtocol()]
)
```

The bus wiring, lifespan management, and router inclusion are all handled automatically by `ExternalConnectionsHandler` (or `InternalConnectionsHandler` for internal protocols).

> The `Handler` abstraction keeps protocol concerns fully isolated from each other and from the core routing logic. Each handler only knows about the bus interface, so adding, removing, or swapping a protocol should have no impact on the rest of the system.

## Development

```bash
uv sync
uv run pytest tests/
```
