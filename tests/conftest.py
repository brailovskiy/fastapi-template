import asyncio
from asyncio import AbstractEventLoop
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Database, PostgresBase
from app.deps import get_database_clients, get_postgres_client
from settings.config import ENV_LOCAL_TEST, Settings, get_settings


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    result = get_settings(env_file_path=ENV_LOCAL_TEST)
    return result


@pytest.fixture(scope="session")
def test_app(test_settings: Settings) -> FastAPI:
    from app.main import get_app

    return get_app(test_settings)


@pytest.fixture(scope="session")
def db_instance(test_settings: Settings) -> Generator[Database, Any, Any]:
    db_async_dsn = test_settings.POSTGRES_SQLALCHEMY_DATABASE_URI
    connect_kwargs = dict(**Database.CONNECT_KWARGS, pool_size=5)
    async_db = Database(
        db_connect_url=db_async_dsn,  # type: ignore
        db_alias="postgres",
        connect_kwargs=connect_kwargs,
        debug=test_settings.DEBUG,
    )
    yield async_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_configure(db_instance: Database) -> AsyncGenerator[AsyncSession, None]:
    await db_instance.drop_tables_by_base(PostgresBase)
    await db_instance.create_tables_by_base(PostgresBase)
    yield  # type: ignore
    await db_instance.drop_tables_by_base(PostgresBase)
    await db_instance.disconnect()


@pytest_asyncio.fixture()
async def rest_client(
    db_instance: Database,
    test_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    def _get_postgres_override() -> Database:
        return db_instance

    def _get_db_clients_override() -> dict[str, Database]:
        return {"postgres": db_instance}

    test_app.dependency_overrides[get_postgres_client] = _get_postgres_override
    test_app.dependency_overrides[get_database_clients] = _get_db_clients_override
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

    test_app.dependency_overrides = {}
