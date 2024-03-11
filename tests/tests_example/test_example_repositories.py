import pytest

from app.core.example.repositories import ExampleDBRepository
from app.core.example.schemas.model_factories import ExampleModelFactory
from app.database import Database

pytestmark = [
    pytest.mark.asyncio,
]


async def test_get_example(db_instance: Database, db_repository: ExampleDBRepository) -> None:
    await ExampleModelFactory.create_async(db_instance)
    result = await db_repository.get_example()
    assert len(result) == 1
