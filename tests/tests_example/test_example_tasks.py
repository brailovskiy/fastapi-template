import pytest
from httpx import AsyncClient

pytestmark = [
    pytest.mark.asyncio,
]


async def test_create_example_task(rest_client: AsyncClient) -> None:
    response = await rest_client.post("/api/v1/examples/tasks/example/new", data={"example_param": "test"})
    assert response.status_code == 200
