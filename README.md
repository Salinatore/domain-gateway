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
