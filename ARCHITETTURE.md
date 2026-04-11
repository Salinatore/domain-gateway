# Architecture & Design Decisions

This document explains the key architectural choices behind `domain-gateway`, a component of [Project-Emerge](https://github.com/Project-Emerge/Project-Emerge-system). It is intended as a reference for contributors and reviewers who want to understand the *why* behind the design, not just the *what*.

---

## Context

`domain-gateway` sits at the boundary between the inner domain of the Emerge system and external clients. Internally, all microservices in the Emerge ecosystem communicate over MQTT. Externally, clients — including future physical robots — may speak HTTP, WebSocket, CoAP, or other protocols. This gateway's job is to bridge those two worlds cleanly, without any protocol concern leaking into another.

```
External Clients
  ├── HTTP        ─┐
  ├── WebSocket   ─┼──► Inbound Bus ──► MQTT Broker
  └── CoAP        ─┘
MQTT Broker ──► Outbound Bus ──► Cache / WebSocket subscribers / CoAP observers / ...
```

---

## Dependency Injection

Constructor injection is applied consistently throughout the codebase. Every component — connections, cache, routers — receives all of its dependencies explicitly via its constructor. Nothing reaches for a global or imports a shared singleton mid-graph. The shape of each component's dependencies is visible at a glance from its `__init__` signature.

The single place where all concrete classes are instantiated and wired together is `Container`, which lives in `core/container.py`. It owns the two buses, the cache, and all connection groups. Swapping any component — for example, replacing `MemoryCache` with a Redis-backed implementation — is a one-line change in `Container`, with no impact on anything else.

```python
# Replacing the cache implementation touches exactly one line:
self._cache: Cache = RedisCache(outbound_bus=self._outbound_bus)
```

`main.py` exposes `create_app(container: Container) -> FastAPI`, a pure factory function that accepts a fully-wired container and returns a configured application. It has no side effects of its own and no knowledge of how dependencies are constructed. The production entry point wires the two together:

```python
# entry point
container = Container()
app = create_app(container)
```

This design makes testing straightforward. The test suite constructs its own `Container` in the fixture, swapping `MQTTConnection` for `MockMQTTConnection` — no monkeypatching. The simplicity of that swap is a direct consequence of the DI design.

---

## Core Architecture

### Two separate message buses

Two distinct `Bus` instances are used: one for messages flowing *inward* (external → MQTT broker) and one for messages flowing *outward* (MQTT broker → external clients).

The two directions represent fundamentally different data flows with different consumers and different semantics. Mixing them on a single bus would risk feedback loops — for example, a message arriving from MQTT being re-published back to MQTT — and would make the flow harder to reason about. Keeping them separate makes directionality explicit and enforced by construction: any component only ever sees the traffic relevant to its role.

### Best-effort delivery on the inbound bus

The `MessageBus` dispatches each published message to its subscribers using independent `asyncio.create_task` calls. Publishers return immediately without waiting for subscribers to finish or confirming delivery.

All requests coming from external connections toward the inner domain are treated as best-effort. This is a deliberate trade-off: it keeps the bus non-blocking and ensures that a slow or failing subscriber cannot stall a publisher. The downside — that delivery order and error propagation are not guaranteed — is acceptable in this context, where the domain itself is the source of truth and the gateway is a transport layer, not a transaction coordinator.

### Cache subscribes to the outbound bus

`MemoryCache` attaches to the *outbound* bus, not the inbound one. It stores only messages that have been confirmed received back from the MQTT broker.

The cache holds what *the domain has said*, not what external clients have requested. Since no other microservice in the Emerge ecosystem maintains a last-value cache, this gateway provides one as a convenience for clients that need the latest known state. By listening on the outbound bus, the cache only stores a value once the message has made the full round-trip through MQTT — ensuring that if a message never reached the broker (e.g. due to a connection failure), it is never cached as if it had.

---

## Extensibility

### `Connection` as the single extension point

Every protocol adapter — HTTP, WebSocket, CoAP, MQTT, and any future protocol — implements the same abstract `Connection` interface, which exposes three things: `start()`, `stop()`, and an optional `router`.

This was designed upfront to make adding new protocols a minimal, localised change. The only file that needs to change when a new protocol is introduced is `Container`, where the new `Connection` instance is registered into the appropriate group (`ExternalConnections` or `InternalConnections`). All lifecycle management, router inclusion, and bus wiring are handled automatically by the composite connection classes. No other part of the system needs to know a new protocol exists.

```python
# Adding a new external protocol is exactly this:
external_connections = ExternalConnections(
    connections=[
        HTTPConnection(...),
        WebsocketConnection(...),
        CoAPConnection(...),
        NewProtocolConnection(...),  # ← this is all that changes
    ]
)
```

### Composite connections as opaque groups

`ExternalConnections` and `InternalConnections` act as composite coordinators. They gather the lifecycle of all their children and merge their routers, presenting a single unified surface to `main.py`.

`main.py` and the application lifespan are completely unaware of individual protocols — they hand off two groups and nothing more. This means the startup/shutdown logic and routing registration never need to change as protocols are added or removed. That concern belongs entirely to the group and its children.

### Topic model layering

Topics are split across three modules: `paths.py` defines the topic path strings and patterns, `payloads.py` defines the Pydantic payload models, and `mappings.py` binds patterns to payload classes for the MQTT dispatcher.

This separation means that when a topic's payload schema changes, only `payloads.py` needs updating — the path and the mapping remain untouched, and all protocol adapters that read from the cache pick up the change automatically since they work against the abstract `TopicPayload` type.

Adding a *new* topic is a broader change by nature: `paths.py`, `payloads.py`, and `mappings.py` all need a new entry, and any protocol adapter with hard-coded endpoints — such as the HTTP routers — must add a new route explicitly. Protocol-agnostic adapters like CoAP's `RobotsSubsite`, which resolve routes dynamically from the path, require no changes for new robot endpoints.

---

## Protocol-Specific Decisions

### CoAP: `2.05 Content` with `{}` on empty cache

CoAP GET requests on valid paths with no cached data return `2.05 Content` with an empty JSON object `{}`, rather than `4.04 Not Found`.

This is a deliberate trade-off specific to CoAP's Observe mechanism. If a client registers an Observe subscription and the server responds with `4.04 Not Found`, the client tears down the observation immediately — meaning a client could not subscribe to a robot's topic before that robot comes online. By returning `2.05 Content` with `{}`, the observation is kept alive from the moment of registration, and the client receives a real notification as soon as the robot publishes its first message, with no need to re-subscribe.

This behaviour is intentionally asymmetric with the HTTP endpoints, which correctly return `404 Not Found` on an empty cache. HTTP clients do not maintain persistent subscriptions, so standard semantics apply there without any trade-off.

---

## Testing Strategy

### `MockMQTTConnection` as a round-trip simulator

The test suite replaces `MQTTConnection` with a `MockMQTTConnection` that echoes every inbound bus message directly onto the outbound bus, with no real MQTT broker involved.

The goal is to simulate the full inbound → outbound round-trip without external infrastructure. Because the cache listens on the outbound bus, the mock ensures that a PUT or publish operation from any protocol immediately makes the value available via GET — exactly as it would in production after the message travels through the broker. This keeps tests self-contained, fast, and free of network dependencies, while still exercising the real application wiring end-to-end.

The simplicity of this mock is itself a consequence of the DI design: because `MQTTConnection` is injected rather than imported, replacing it in tests requires no patching whatsoever.

---
