import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar

from kombu import Exchange, Queue
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

PROJ_ROOT = Path(__file__).parent.parent

ENV = PROJ_ROOT / "settings" / ".env"
ENV_CI = PROJ_ROOT / "settings" / ".env.ci"
ENV_LOCAL_TEST = PROJ_ROOT / "settings" / ".env.test"
ENV_TEST = PROJ_ROOT / "settings" / ".env.test"


class LogTypeEnum(str, Enum):
    JSON = "json"
    PLAIN = "plain"


class LogLevelEnum(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = ""


class DBSettings(BaseSettings):
    ASYNC_POSTGRES_DRIVER_NAME: str = "postgresql+asyncpg"
    CELERY_POSTGRES_DRIVER_NAME: str = "db+postgresql"
    DB_READABLE_NAMES: list[str] = ["POSTGRES"]

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "postgrespwd"
    POSTGRES_DB: str = "example"
    POSTGRES_POOL_SIZE: int = 5

    POSTGRES_SQLALCHEMY_DATABASE_URI: URL = None  # type: ignore[assignment]

    @staticmethod
    def _make_db_uri(
        prefix: str,
        driver: str,
        value: str | None,
        values: dict[str, Any],
    ) -> URL:
        """
        Возвращает uri для заданной базы
        Args:
            prefix: str - префикс в названии заданной базы
            driver: str - драйвер, используемый для коннекта к базе
            value: str | None - значение, переданное в валидируемое поле
            values: Dict[str, Any] - словарь значений переданных в модель

        Returns:
            str - uri для заданного шарда dbp
        """
        if isinstance(value, str):
            return URL.value  # type: ignore[attr-defined]

        return URL.create(
            drivername=driver,
            database=values.get(f"{prefix}_DB"),
            username=values.get(f"{prefix}_USER"),
            password=values.get(f"{prefix}_PASSWORD"),
            host=values.get(f"{prefix}_HOST"),
            port=values.get(f"{prefix}_PORT"),
        )

    @field_validator("POSTGRES_SQLALCHEMY_DATABASE_URI", mode="before")
    def postgres_dsn(cls, value: str | None, values: ValidationInfo) -> URL:
        return cls._make_db_uri(
            prefix="POSTGRES",
            driver=values.data["ASYNC_POSTGRES_DRIVER_NAME"],
            value=value,
            values=values.data,
        )


class OpenAPISettings(BaseSettings):
    OPENAPI_URL: str = "/openapi.json"
    OPENAPI_FETCHING_SERVER: str = "/"


class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str = "amqp://guest:guest@127.0.0.1:5672/"
    CELERY_BROKER_CONNECTION_MAX_RETRIES: int | None = None
    CELERY_BROKER_POOL_LIMIT: int | None = None

    CELERY_ENABLE_UTC: bool = True
    CELERY_TIMEZONE: str = "UTC"

    CELERY_ALWAYS_EAGER: bool = False

    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 10_000
    CELERY_WORKER_MAX_MEMORY_PER_CHILD: int = 500_000  # 500 MB
    CELERY_WORKER_HIJACK_ROOT_LOGGER: bool = False

    CELERY_ACCEPT_CONTENT: ClassVar = ["xjson"]
    CELERY_TASK_SERIALIZER: ClassVar = "xjson"
    CELERY_RESULT_SERIALIZER: ClassVar = "xjson"

    CELERY_TASK_DEFAULT_QUEUE: str = "default"
    task_default_queue: str = "default"
    task_create_missing_queues: bool = True
    task_queues: list[Queue] = [
        Queue(
            task_default_queue,
            Exchange("default"),
            routing_key="default",
            queue_arguments={"x-max-priority": 12},
        ),
    ]


class Settings(
    CelerySettings,
    DBSettings,
    OpenAPISettings,
):
    PROJECT_NAME: str = "fastapi_template"
    APP_HOST: str
    APP_PORT: int
    STAGE: str = "dev"
    DEBUG: bool = False

    LOG_LEVEL: LogLevelEnum
    JSON_LOG: bool

    model_config = SettingsConfigDict(env_file=ENV, populate_by_name=True)


def dump_config(config: Settings) -> str:
    return config.model_dump_json(indent=2, exclude={"task_queues"})


@lru_cache
def get_settings(env_file_path: Path | None = None) -> Settings:
    if env_file := os.getenv("ENV_FILE"):
        return Settings(_env_file=env_file)
    if env_file_path:
        return Settings(_env_file=env_file_path)
    return Settings()
