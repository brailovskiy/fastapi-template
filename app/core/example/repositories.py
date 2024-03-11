from dataclasses import dataclass

from pydantic import TypeAdapter
from sqlalchemy import select

from app.core.base.base_repositories import BasePostgresRepository
from app.core.example.models import Example
from app.core.example.schemas.dto import ExampleDTO


@dataclass
class ExampleDBRepository(BasePostgresRepository):
    async def get_example(self) -> list[ExampleDTO]:
        query = select(Example)
        query_result = await self._execute_query_and_return_scalars(query)

        type_annotation = TypeAdapter(list[ExampleDTO])
        result = type_annotation.validate_python(query_result)

        return result

    async def get_one_by_id(self, id_: int) -> ExampleDTO | None:
        query = select(Example).where(Example.id == id_)
        query_result = await self._execute_query_and_return_scalar(query)

        if query_result:
            result = ExampleDTO.model_validate(query_result)
        else:
            result = None

        return result
