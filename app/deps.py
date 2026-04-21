from typing import Any

from fastapi.requests import Request

from app.database import Database


def get_database_clients(request: Request) -> dict[str, Database]:
    return request.app.state.databases


def get_postgres_client(request: Request, database_alias: str = "postgres") -> dict[str, Any]:
    """Dependencies with parameter."""

    return request.app.state.databases[database_alias.upper()]
