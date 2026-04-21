import asyncio

from celery import Task

from app.core.example.repositories import ExampleDBRepository
from app.core.example.services import ExampleService
from app.database import Database
from settings.config import Settings, get_settings


class CeleryTask(Task):
    abstract = True

    def __init__(self) -> None:
        self.settings: Settings = get_settings()
        self.database: Database = get_database()
        self._loop = None

    @property
    def loop(self):
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop


def get_database(db_alias: str = "POSTGRES") -> Database:
    settings: Settings = get_settings()
    return Database(
        db_connect_url=getattr(settings, f"{db_alias}_SQLALCHEMY_DATABASE_URI"),
        db_alias=db_alias,
        connect_kwargs=dict(**Database.CONNECT_KWARGS, pool_size=getattr(settings, f"{db_alias}_POOL_SIZE")),
        debug=settings.DEBUG,
    )


def get_example_database_repository() -> ExampleDBRepository:
    return ExampleDBRepository(postgres=get_database())


def get_example_service() -> ExampleService:
    return ExampleService(repository=get_example_database_repository())
