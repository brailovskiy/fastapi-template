import asyncio
from typing import Any

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from app.database import Database
from app.deps import get_database_clients

system_router = APIRouter()


@system_router.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
    description="Healthcheck service",
    name="system:healthcheck",
)
async def healthcheck() -> dict[str, Any]:
    return {}


@system_router.get(
    "/readiness-check",
    status_code=status.HTTP_200_OK,
    description="Readiness check service",
    name="system:readiness-check",
)
async def readiness_check(databases: dict[str, Database] = Depends(get_database_clients)) -> JSONResponse:
    db_statuses = await asyncio.gather(*[db.get_status() for db in databases.values()])
    response = {"databases": db_statuses}
    return JSONResponse(response, status_code=status.HTTP_200_OK)
