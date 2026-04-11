WebSocket subscription leak	Memory leak	Clean up on disconnect
Unbounded MQTT queue	Crash risk	Set maxsize + backpressure
Hard‑coded CoAP bind address	Deployment pain	Make configurable
No unsubscribe in bus	Testing / dynamic	Add unsubscribe
Stale WebSocket subscriptions on error	Resource waste	Remove on send failure
CoAP port conflict not handled	Startup failure	Catch and log / retry
HTTP endpoints block on publish	Poor UX	Decouple via async bus
No observability	Operability	Add health/metrics endpoints
