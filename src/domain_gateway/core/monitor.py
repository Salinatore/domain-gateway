from enum import StrEnum
from typing import NamedTuple, Protocol


class Status(StrEnum):
    """Enumeration of possible connection health statuses.

    Attributes:
        UP: The connection is running and healthy.
        DOWN: The connection is not running or has failed.
    """

    UP = "UP"
    DOWN = "DOWN"


class _ConnectionEntry(NamedTuple):
    """Internal record holding the health state of a single registered connection.

    Attributes:
        status: Current health status of the connection.
        critical: Whether this connection being DOWN makes the whole system unhealthy.
    """

    status: Status
    critical: bool


class HealthHandle:
    """A scoped write-only handle injected into a single connection.

    Intentionally exposes only ``report``, so the owning connection cannot
    inspect or influence the health state of other connections, and does not
    need to know whether it is considered critical.

    Attributes:
        _key: The connection class used as the registry key in the monitor.
        _monitor: The shared HealthMonitor that owns the underlying state.
    """

    def __init__(self, key: type, monitor: "HealthMonitor") -> None:
        """Initialise the handle with its registry key and owning monitor.

        Args:
            key: The connection class this handle represents.
            monitor: The HealthMonitor that will receive status updates.
        """
        self._key = key
        self._monitor = monitor

    def report(self, status: Status) -> None:
        """Push a new status for this connection to the monitor.

        Args:
            status: The new health status to record.
        """
        self._monitor._update(self._key, status)


class HealthMonitor:
    """Central registry that tracks the health of all registered connections.

    Connections are registered at startup via ``register``, which returns a
    ``HealthHandle`` for that connection to report its own status. The monitor
    exposes aggregate health (``is_healthy``) and a per-connection snapshot
    suitable for a health-check endpoint.

    Attributes:
        _connections: Mapping from connection class to its current health entry.
    """

    def __init__(self) -> None:
        """Initialise the monitor with an empty connection registry."""
        self._connections: dict[type, _ConnectionEntry] = {}

    def register(self, connection_class: type, *, critical: bool) -> HealthHandle:
        """Register a connection class and return a handle for it to report status.

        The connection is registered with an initial status of ``DOWN``.

        Args:
            connection_class: The class of the connection being registered.
            critical: If ``True``, this connection being DOWN will cause
                ``is_healthy`` to return ``False``.

        Returns:
            A ``HealthHandle`` scoped to the given connection class.
        """
        self._connections[connection_class] = _ConnectionEntry(
            status=Status.DOWN,
            critical=critical,
        )
        return HealthHandle(connection_class, self)

    def _update(self, key: type, status: Status) -> None:
        """Update the status of a previously registered connection.

        Args:
            key: The connection class whose status is being updated.
            status: The new health status to store.
        """
        entry = self._connections[key]
        self._connections[key] = _ConnectionEntry(
            status=status,
            critical=entry.critical,
        )

    def is_healthy(self) -> bool:
        """Return whether all critical connections are currently UP.

        Returns:
            ``True`` if every critical connection has status ``UP``,
            ``False`` if any critical connection is ``DOWN``.
        """
        return all(
            entry.status == Status.UP
            for entry in self._connections.values()
            if entry.critical
        )

    def snapshot(self) -> dict[str, dict]:
        """Return a status snapshot of every registered connection.

        Intended for use in a health-check HTTP response body.

        Returns:
            A dict mapping each connection class name to a dict containing
            ``status`` and ``critical`` fields.
        """
        return {
            cls.__name__: {"status": entry.status, "critical": entry.critical}
            for cls, entry in self._connections.items()
        }


class HealthReporter(Protocol):
    """Read-only protocol for components that only need to query health state.

    Used to decouple consumers (e.g. HTTP health endpoints) from the concrete
    ``HealthMonitor`` implementation.
    """

    def is_healthy(self) -> bool:
        """Return whether the system is considered healthy."""
        ...

    def snapshot(self) -> dict[str, dict]:
        """Return a per-connection status snapshot."""
        ...
