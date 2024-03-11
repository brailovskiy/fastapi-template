from fastapi.requests import Request

from app.database import Database


def get_database_clients(request: Request) -> dict[str, Database]:
    return request.app.state.databases


def get_postgres_client(database_alias: str = 'postgres'):
    """Dependencies with parameter."""

    def dependency(request: Request):
        return request.app.state.databases[database_alias]

    return dependency
