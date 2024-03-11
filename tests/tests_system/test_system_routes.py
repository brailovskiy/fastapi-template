import pytest
from httpx import AsyncClient

pytestmark = [
    pytest.mark.asyncio,
]


async def test_get_healthcheck(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/v1/healthcheck")
    assert response.status_code == 200


async def test_get_docs(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/openapi.json")
    assert response.status_code == 200


async def test_get_readiness_check(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/v1/readiness-check")
    assert response.status_code == 200
    assert response.json() == {
        "databases": [
            {
                "name": "postgres",
                "status": "ready",
            },
        ],
    }
