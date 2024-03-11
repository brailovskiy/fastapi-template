from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette import status
from starlette.responses import Response

from app.celery_app.celery_executor import CeleryTasksExecutor
from app.celery_app.tasks import example_task
from app.core.base.base_deps import get_celery_tasks_executor
from app.core.example.deps import get_example_service
from app.core.example.schemas.dto import ExampleDTO
from app.core.example.services import ExampleService

example_router: APIRouter = APIRouter()


@example_router.post(
    "/tasks/example/new",
    status_code=status.HTTP_200_OK,
    description="Create example task",
)
async def create_example_task(
    example_param: str = "example",
    celery_tasks_executor: CeleryTasksExecutor = Depends(get_celery_tasks_executor),
) -> Response:
    await celery_tasks_executor.run(
        example_task,
        params={"example_param": example_param},
    )
    logger.info("test_task_scheduled by API with example_param: {example_param}", example_param=example_param)
    return Response(status_code=status.HTTP_200_OK)


@example_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    description="Get all models Example",
    name="examples:get-all-by-id",
)
async def get_list_example(service: ExampleService = Depends(get_example_service)) -> list[ExampleDTO]:
    items = await service.get_all_items()

    return items


@example_router.get(
    "/{example_id:int}",
    status_code=status.HTTP_200_OK,
    description="Get one model example by id",
    name="examples:get-one-by-id",
)
async def get_one_example(example_id: int, service: ExampleService = Depends(get_example_service)) -> ExampleDTO:
    item = await service.get_one_item(example_id)
    if not item:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="File with this parameters not found for you",
        )

    return item
