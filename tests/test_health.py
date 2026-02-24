import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_welcome(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Employee Management System"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}