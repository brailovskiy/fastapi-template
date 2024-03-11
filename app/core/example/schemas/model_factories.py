from app.core.base.base_factories import AbstractModelFactory
from app.core.example.models import Example
from app.core.example.schemas.dto import ExampleDTO


class ExampleModelFactory(AbstractModelFactory[Example]):
    __model__ = ExampleDTO
    __orm_model__ = Example
