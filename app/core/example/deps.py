from fastapi import Depends

from app.core.example.repositories import ExampleDBRepository
from app.core.example.services import ExampleService
from app.database import Database
from app.deps import get_postgres_client


def get_example_database_repository(postgres: Database = Depends(get_postgres_client())) -> ExampleDBRepository:
    return ExampleDBRepository(postgres=postgres)


def get_example_service(repository: ExampleDBRepository = Depends(get_example_database_repository)) -> ExampleService:
    return ExampleService(repository=repository)
