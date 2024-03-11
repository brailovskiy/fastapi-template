import pytest

from app.core.example.repositories import ExampleDBRepository
from app.database import Database


@pytest.fixture(scope="session")
def db_repository(db_instance: Database) -> ExampleDBRepository:
    return ExampleDBRepository(postgres=db_instance)
