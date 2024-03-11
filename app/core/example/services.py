from dataclasses import dataclass

from loguru import logger

from app.core.example.repositories import ExampleDBRepository
from app.core.example.schemas.dto import ExampleDTO


@dataclass
class ExampleService:
    repository: ExampleDBRepository

    @staticmethod
    async def create_test_task(example_param: str = "example") -> None:
        logger.info("test_task_scheduled with example_param: {example_param}", example_param=example_param)

    async def get_one_item(self, id_: int) -> ExampleDTO | None:
        item = await self.repository.get_one_by_id(id_)

        return item

    async def get_all_items(self) -> list[ExampleDTO]:
        item = await self.repository.get_example()

        return item
