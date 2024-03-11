from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.sql import Select, Update

from app.database import Database


@dataclass
class BasePostgresRepository:
    postgres: Database

    async def bulk_create_objects(self, objects: Iterable[Any]) -> None:
        async with self.postgres.session() as async_session:
            async_session.add_all(objects)
            await async_session.commit()

    async def _execute_query_and_return_result(self, query: Select | Update) -> Any:
        async with self.postgres.session() as async_session:
            result = await async_session.execute(query)
            await async_session.commit()
        return result

    async def _execute_query_and_return_scalar(self, query: Select) -> Any:
        return (await self._execute_query_and_return_result(query)).scalar()

    async def _execute_query_and_return_scalars(self, query: Select) -> list[Any]:
        return (await self._execute_query_and_return_result(query)).scalars().all()
