from typing import TYPE_CHECKING, Any

from anyio import Semaphore
from loguru import logger
from starlette.concurrency import run_in_threadpool

from app.celery_app.constants import MAX_CONCURRENT_THREADS

if TYPE_CHECKING:
    from app.celery_app.celery_deps import CeleryTask

logger = logger.bind(context="celery_tasks")


class CeleryTasksExecutor:
    def __init__(self, max_concurrent_thread: int = MAX_CONCURRENT_THREADS) -> None:
        self._max_threads_guard = Semaphore(max_concurrent_thread)

    async def run(self, func: "CeleryTask", params: dict[str, Any]) -> None:
        async with self._max_threads_guard:
            await run_in_threadpool(func.apply_async, kwargs=params)
