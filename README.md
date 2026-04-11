# Domain Gateway

Protocol-agnostic gateway for bidirectional communication between external clients and the inner domain. Part of [Project-Emerge](https://github.com/Project-Emerge), specifically the [Project-Emerge-system](https://github.com/Project-Emerge/Project-Emerge-system).

## Overview

The gateway bridges external protocols (HTTP, WebSocket, CoAP) with the internal MQTT-based domain. It routes messages through an internal bus and maintains a cache of the latest topic payloads.

```
External Clients
  ├── HTTP        ─┐
  ├── WebSocket   ─┼──► Inbound Bus ──► MQTT Broker
  └── CoAP        ─┘
MQTT Broker ──► Outbound Bus ──► Cache / WebSocket subscribers / Coap observerers / others
```

## Protocols

| Protocol  | Type            | Use case                            |
|-----------|-----------------|-------------------------------------|
| HTTP      | External        | REST-style reads and writes         |
| WebSocket | External        | Real-time subscriptions             |
| CoAP      | External        | Constrained device communication    |
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

## CoAP API

Server binds to `coap://0.0.0.0:5683` by default.

### Robots — `/robots/{id}/{endpoint}`

All endpoints return `application/json` (Content-Format 50).

GET on an unknown path returns `4.04 Not Found`.  
GET on a valid path with no data yet returns `2.05 Content` with `{}` — this keeps
Observe registrations alive so clients can subscribe before a robot comes online.

| Endpoint    | GET                                        | PUT                        | Observe |
|-------------|--------------------------------------------|----------------------------|---------|
| `position`  | Latest `RobotPosition`, `{}` if not set   | Publish `RobotPosition`    | ✓       |
| `movement`  | Latest `RobotMovement`, `{}` if not set   | Publish `RobotMovement`    | ✓       |
| `neighbors` | Latest `RobotNeighbors`, `{}` if not set  | Publish `RobotNeighbors`   | ✓       |
| `sensing`   | Latest `RobotSensing`, `{}` if not set    | Publish `RobotSensing`     | ✓       |

### Computing — `/computing/inputs/{resource}`

| Resource    | GET                                       | PUT                     | Observe |
|-------------|-------------------------------------------|-------------------------|---------|
| `formation` | Latest `Formation`, `{}` if not set      | Publish `Formation`     | ✓       |
| `leader`    | Latest `Leader`, `{}` if not set         | Publish `Leader`        | ✓       |

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

The architecture is built around a single `Connection` abstract class. Adding a new protocol means implementing the interface and registering the handler.

```python
external_connections = ExternalConnections(
    connections=[HTTPConnection(), WebsocketConnection(), CoAPConnection(cache=cache), NewConnection()]
)
```

The bus wiring, lifespan management, and router inclusion are all handled automatically by `ExternalConnections` (or `InternalConnections` for internal protocols).

> The `Connection` abstraction keeps protocol concerns fully isolated from each other and from the core routing logic. Each connection only knows about the bus interface, so adding, removing, or swapping a protocol should have no impact on the rest of the system.
