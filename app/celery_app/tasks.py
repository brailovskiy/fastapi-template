from loguru import logger

from app.celery_app.celery_app import celery
from app.celery_app.celery_deps import CeleryTask, get_example_service

logger = logger.bind(context="celery_tasks")


@celery.task(name="example_task", bind=True, base=CeleryTask)
def example_task(self: CeleryTask, example_param: str = "example") -> None:
    async def task() -> None:
        example_service = get_example_service()
        await example_service.create_test_task(example_param=example_param)

    self.loop.run_until_complete(task())
