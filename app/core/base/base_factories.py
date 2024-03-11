from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.inspection import inspect

from app.database import Database

_OrmModel = TypeVar("_OrmModel")
_PydanticModel = TypeVar("_PydanticModel", bound=BaseModel)


class AsyncPersistenceHandler(Generic[_OrmModel]):
    def __init__(self, db: Database, orm_model: type[_OrmModel]) -> None:
        self.db = db
        self.orm_model = orm_model

    async def save_many(self, data: list[_PydanticModel]) -> list[_OrmModel]:
        objects = [self.orm_model(**task_dto.model_dump()) for task_dto in data]
        async with self.db.session() as session:
            session.add_all(objects)
            await session.commit()
        return objects

    async def refresh(self, objs: list[_OrmModel]) -> list[Any]:
        result = []
        async with self.db.session() as session:
            for obj in objs:
                primary_keys = inspect(obj.__class__).primary_key  # type: ignore[union-attr]
                query = select(obj.__class__).where(
                    and_(*{getattr(obj.__class__, pk.key) == getattr(obj, pk.key) for pk in primary_keys}),
                )
                created = await session.execute(query)
                result.append(created.scalars().first())
        return result


class AbstractModelFactory(ModelFactory[Any], Generic[_OrmModel]):
    """Генерирует и создаёт в БД запись. При необходимости, можно передать
    через kwargs значения, которые должны быть не сгенерированы, а присвоены.

    Использование:
        class Foo(PostgresBase):
            ...

        class FooDTO(BaseModel):
            ...

        class FooFactory(AbstractModelFactory[Foo]):
            __model__ = FooDTO
            __orm_model__ = Foo

        await FooFactory.create_async(db_instance, **kwargs) - создаёт//генерирует Foo объект
        await FooFactory.create_batch_async(db_instance, n, **kwargs) - создаёт//генерирует n Foo объектов
        await FooFactory.refresh_async(db_instance, **kwargs) - обновляет Foo объекты из БД
    """

    __async_persistence__: type[AsyncPersistenceHandler] = AsyncPersistenceHandler  # type: ignore
    __orm_model__: type[_OrmModel]
    __is_base_factory__ = True

    @classmethod
    async def create_batch_async(cls, db: Database, size: int, **kwargs: Any) -> list[_OrmModel]:  # type: ignore
        async_persistence_handler = cls.__async_persistence__(db, cls.__orm_model__)
        batch = cls.batch(size, **kwargs)
        result = await async_persistence_handler.save_many(data=batch)
        return await async_persistence_handler.refresh(result)

    @classmethod
    async def create_async(cls, db: Database, **kwargs: Any) -> _OrmModel:  # type: ignore
        async_persistence_handler = cls.__async_persistence__(db, cls.__orm_model__)
        instance = cls.build(**kwargs)
        result = await async_persistence_handler.save_many(data=[instance])
        result = await async_persistence_handler.refresh(result)
        return result[0]

    @classmethod
    async def create_batch_from_instances(cls, db: Database, instances: Iterable[Any]) -> list[_OrmModel]:
        async_persistence_handler = cls.__async_persistence__(db, cls.__orm_model__)
        result = await async_persistence_handler.save_many(data=list(instances))
        result = await async_persistence_handler.refresh(result)
        return result

    @classmethod
    async def refresh_async(cls, db: Database, objects: _OrmModel | list[_OrmModel]) -> list[_OrmModel] | _OrmModel:
        async_persistence_handler = cls.__async_persistence__(db, cls.__orm_model__)
        if not isinstance(objects, list):
            objects = [objects]
        result = await async_persistence_handler.refresh(objs=objects)
        if len(result) == 1:
            return result[0]
        return result
