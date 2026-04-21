from collections.abc import Callable
from typing import Any

from celery import Celery
from celery.signals import setup_logging
from kombu.serialization import register
from starlette.concurrency import run_in_threadpool

from app.celery_app.constants import MAX_THREADS_GUARD
from app.utils import xjson
from app.utils.log_handler import init_logging
from settings.config import get_settings


@setup_logging.connect
def configure_workers_logging(sender: Any | None = None, **kwargs: Any) -> None:
    """Override celery's logging setup to prevent it from altering our
    settings.

    https://github.com/celery/celery/issues/1867
    """
    init_logging(get_settings())


register("xjson", xjson.dumps, xjson.loads, content_type="application/x-xjson", content_encoding="utf-8")

settings = get_settings()
celery = Celery("celery_app")

celery.config_from_object(settings.model_dump(by_alias=True), namespace="CELERY")

celery.conf.accept_content = ["json", "xjson"]
celery.conf.task_serializer = "json"  # Для теста используем json
celery.conf.result_serializer = "json"

celery.autodiscover_tasks(["app.celery_app"])

celery.conf.beat_schedule = {
    "example_task": {
        "task": "example_task", # Это имя из @celery.task(name="example_task")
        "schedule": 10.0,
    },
}

async def run_in_background(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func.apply_async, args, kwargs)  # type: ignore
