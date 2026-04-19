from typing import Any, override

from fastapi import APIRouter, Depends, HTTPException, status

from domain_gateway.connections.externals.connections.http.routers.computing import (
    ComputingRouter,
)
from domain_gateway.connections.externals.connections.http.routers.robots import (
    RobotRouter,
)
from domain_gateway.core.bus import Bus
from domain_gateway.core.cache import Cache
from domain_gateway.core.connection import Connection
from domain_gateway.core.monitor import HealthReporter

_HEALTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_503_SERVICE_UNAVAILABLE: {
        "description": "One or more critical connections are down",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "MQTTConnection": {"status": "DOWN", "critical": True},
                        "CoAPConnection": {"status": "UP", "critical": False},
                    }
                }
            }
        },
    }
}


class HTTPConnection(Connection):
    def __init__(
        self,
        root_router: APIRouter,
        cache: Cache,
        inbound_bus: Bus,
        outbound_bus: Bus,
        health_checkable: HealthReporter,
    ):
        async def check_health() -> None:
            if not health_checkable.is_healthy():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=health_checkable.snapshot(),
                )

        health_dependency = Depends(check_health)

        root_router.include_router(
            RobotRouter(cache=cache, inbound_bus=inbound_bus).router,
            dependencies=[health_dependency],
            responses=_HEALTH_RESPONSES,
        )
        root_router.include_router(
            ComputingRouter(cache=cache, inbound_bus=inbound_bus).router,
            dependencies=[health_dependency],
            responses=_HEALTH_RESPONSES,
        )

    @override
    async def start(self) -> None:
        pass

    @override
    async def stop(self) -> None:
        pass
