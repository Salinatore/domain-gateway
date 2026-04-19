# src/domain_gateway/core/monitor.py

from enum import StrEnum
from typing import NamedTuple, Protocol


class Status(StrEnum):
    UP = "UP"
    DOWN = "DOWN"


class _ConnectionEntry(NamedTuple):
    status: Status
    critical: bool


class HealthHandle:
    """Injected into a connection. The connection only knows about this —
    not whether it's critical, not what other connections exist."""

    def __init__(self, key: type, monitor: "HealthMonitor") -> None:
        self._key = key
        self._monitor = monitor

    def report(self, status: Status) -> None:
        self._monitor._update(self._key, status)


class HealthMonitor:
    def __init__(self) -> None:
        self._connections: dict[type, _ConnectionEntry] = {}

    def register(self, connection_class: type, *, critical: bool) -> HealthHandle:
        """Called from Container. Registers a connection and returns a handle to inject."""
        self._connections[connection_class] = _ConnectionEntry(
            status=Status.DOWN,  # DOWN as default
            critical=critical,
        )
        return HealthHandle(connection_class, self)

    def _update(self, key: type, status: Status) -> None:
        entry = self._connections[key]
        self._connections[key] = _ConnectionEntry(
            status=status,
            critical=entry.critical,
        )

    def is_healthy(self) -> bool:
        """False if any critical connection is DOWN."""
        return all(
            entry.status == Status.UP
            for entry in self._connections.values()
            if entry.critical
        )

    def snapshot(self) -> dict[str, dict]:
        """Per-connection status, for GET /health response body."""
        return {
            cls.__name__: {"status": entry.status, "critical": entry.critical}
            for cls, entry in self._connections.items()
        }


class HealthReporter(Protocol):
    def is_healthy(self) -> bool: ...
    def snapshot(self) -> dict[str, dict]: ...
