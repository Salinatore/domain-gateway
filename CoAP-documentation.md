# CoAP API Documentation

All resources are exposed via CoAP over UDP.  
Base URI: `coap://<host>/<resource>`

All payloads are JSON encoded (`Content-Format: 50`).

---

## General Notes

### Observe (RFC 7641)
All resources in this API are **Observe-only** — plain GET requests without the Observe option are rejected with `4.05 Method Not Allowed`.  
The server acts as a pure broker: it does not hold the latest value, so the first notification is sent only when the next MQTT message arrives on the corresponding topic.

To **register** an observation:
```
GET coap://<host>/<resource>  [Observe: 0]
```

To **deregister**:
```
GET coap://<host>/<resource>  [Observe: 1]
```

### Response Codes

| Code | Meaning |
|------|---------|
| `2.05 Content` | Notification with payload |
| `4.05 Method Not Allowed` | Plain GET without Observe option |
| `4.04 Not Found` | Robot ID does not exist |

---

## Resources

### 1. Robot Position

**URI:** `coap://<host>/robots/{robot_id}/position`

Subscribe to position updates for a specific robot or all robots.

| Parameter | Type | Description |
|-----------|------|-------------|
| `robot_id` | integer or `+` | A specific robot ID, or `+` to observe all robots |

**Notification payload:**
```json
{
  "robot_id": 42,
  "x": 1.23,
  "y": 4.56,
  "orientation": 0.78
}
```

| Field | Type | Description |
|-------|------|-------------|
| `robot_id` | integer | The ID of the robot |
| `x` | float | X position |
| `y` | float | Y position |
| `orientation` | float | Yaw around Z axis, in radians |

**MQTT topic:** `robots/{id}/position`

---

### 2. Robot Neighbors

**URI:** `coap://<host>/robots/{robot_id}/neighbors`

Subscribe to neighbor updates for a specific robot or all robots.

| Parameter | Type | Description |
|-----------|------|-------------|
| `robot_id` | integer or `+` | A specific robot ID, or `+` to observe all robots |

**Notification payload:**
```json
{
  "neighbors": [1, 3, 7]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `neighbors` | list of integers | IDs of the neighboring robots |

**MQTT topic:** `robots/{id}/neighbors`

---

### 3. Robot Movement

**URI:** `coap://<host>/robots/{robot_id}/move`

Subscribe to movement commands for a specific robot or all robots.

| Parameter | Type | Description |
|-----------|------|-------------|
| `robot_id` | integer or `+` | A specific robot ID, or `+` to observe all robots |

**Notification payload:**
```json
{
  "left": 0.5,
  "right": -0.5
}
```

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `left` | float | [-1.0, 1.0] | Left wheel speed |
| `right` | float | [-1.0, 1.0] | Right wheel speed |

**MQTT topic:** `robots/{id}/move`

---

### 4. Leader Command

**URI:** `coap://<host>/leader`

Subscribe to leader commands for the robot swarm.

**Notification payload:**
```json
{
  "leader_id": 3
}
```

| Field | Type | Description |
|-------|------|-------------|
| `leader_id` | integer | ID of the robot designated as leader |

**MQTT topic:** `leader`

---

### 5. Sensing Command

**URI:** `coap://<host>/sensing`

Subscribe to sensing/formation commands for the robot swarm.

**Notification payload:**
```json
{
  "program": "vShape",
  "leader": 2,
  "collisionArea": 0.5,
  "stabilityThreshold": 0.1,
  "interDistanceV": 1.0,
  "angleV": 45.0
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `program` | string | ✅ | Formation program name (e.g. `pointToLeader`, `vShape`, `circle`, `square`, `line`, `verticalLine`) |
| `leader` | integer | ❌ | ID of the leader robot |
| `collisionArea` | float | ❌ | Collision avoidance area |
| `stabilityThreshold` | float | ❌ | Stability threshold |
| `interDistanceLine` | float | ❌ | Inter-robot distance for line formation |
| `interDistanceVertical` | float | ❌ | Inter-robot distance for vertical line formation |
| `interDistanceV` | float | ❌ | Inter-robot distance for V formation |
| `angleV` | float | ❌ | Angle for V formation |
| `radius` | float | ❌ | Radius for circle formation |
| `interDistanceSquare` | float | ❌ | Inter-robot distance for square formation |

> Fields use **camelCase** in the JSON payload.

**MQTT topic:** `sensing`
