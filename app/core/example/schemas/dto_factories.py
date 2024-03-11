from polyfactory.factories.pydantic_factory import ModelFactory

from app.core.example.schemas.dto import ExampleDTO


class ExampleDTOFactory(ModelFactory[ExampleDTO]):
    __model__ = ExampleDTO
