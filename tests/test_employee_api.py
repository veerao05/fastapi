import pytest
from httpx import AsyncClient

EMPLOYEE_URL = "/api/employees/"

SAMPLE_EMPLOYEE = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "salary": 75000.0,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def create_employee(client: AsyncClient, data: dict = None) -> dict:
    payload = data or SAMPLE_EMPLOYEE
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 201
    return response.json()


# ── Create ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_employee_success(client: AsyncClient):
    response = await client.post(EMPLOYEE_URL, json=SAMPLE_EMPLOYEE)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["department"] == "Engineering"
    assert data["salary"] == 75000.0
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_employee_invalid_email(client: AsyncClient):
    payload = {**SAMPLE_EMPLOYEE, "email": "not-an-email"}
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_negative_salary(client: AsyncClient):
    payload = {**SAMPLE_EMPLOYEE, "salary": -500.0}
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_zero_salary(client: AsyncClient):
    payload = {**SAMPLE_EMPLOYEE, "salary": 0}
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_empty_name(client: AsyncClient):
    payload = {**SAMPLE_EMPLOYEE, "name": ""}
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_name_too_long(client: AsyncClient):
    payload = {**SAMPLE_EMPLOYEE, "name": "a" * 101}
    response = await client.post(EMPLOYEE_URL, json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_missing_required_fields(client: AsyncClient):
    response = await client.post(EMPLOYEE_URL, json={"name": "John"})
    assert response.status_code == 422


# ── Get All ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_all_employees_empty(client: AsyncClient):
    response = await client.get(EMPLOYEE_URL)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_employees(client: AsyncClient):
    await create_employee(client)
    await create_employee(client, {**SAMPLE_EMPLOYEE, "email": "jane.smith@example.com", "name": "Jane Smith"})

    response = await client.get(EMPLOYEE_URL)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ── Get By ID ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_employee_by_id_success(client: AsyncClient):
    created = await create_employee(client)
    response = await client.get(f"{EMPLOYEE_URL}{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == "John Doe"


@pytest.mark.asyncio
async def test_get_employee_by_id_not_found(client: AsyncClient):
    response = await client.get(f"{EMPLOYEE_URL}999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_employee_success(client: AsyncClient):
    created = await create_employee(client)
    response = await client.put(
        f"{EMPLOYEE_URL}{created['id']}",
        json={"name": "John Smith", "salary": 90000.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["salary"] == 90000.0
    assert data["email"] == SAMPLE_EMPLOYEE["email"]  # unchanged


@pytest.mark.asyncio
async def test_update_employee_partial(client: AsyncClient):
    created = await create_employee(client)
    response = await client.put(
        f"{EMPLOYEE_URL}{created['id']}",
        json={"salary": 85000.0},
    )
    assert response.status_code == 200
    assert response.json()["salary"] == 85000.0
    assert response.json()["name"] == "John Doe"  # unchanged


@pytest.mark.asyncio
async def test_update_employee_not_found(client: AsyncClient):
    response = await client.put(f"{EMPLOYEE_URL}999", json={"name": "Ghost"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


@pytest.mark.asyncio
async def test_update_employee_invalid_salary(client: AsyncClient):
    created = await create_employee(client)
    response = await client.put(
        f"{EMPLOYEE_URL}{created['id']}",
        json={"salary": -100.0},
    )
    assert response.status_code == 422


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_employee_success(client: AsyncClient):
    created = await create_employee(client)
    response = await client.delete(f"{EMPLOYEE_URL}{created['id']}")
    assert response.status_code == 204

    # Confirm it's gone
    get_response = await client.get(f"{EMPLOYEE_URL}{created['id']}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_employee_not_found(client: AsyncClient):
    response = await client.delete(f"{EMPLOYEE_URL}999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_employee_full_lifecycle(client: AsyncClient):
    # Create
    created = await create_employee(client)
    employee_id = created["id"]

    # Read
    get_resp = await client.get(f"{EMPLOYEE_URL}{employee_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "John Doe"

    # Update
    update_resp = await client.put(
        f"{EMPLOYEE_URL}{employee_id}",
        json={"department": "DevOps", "salary": 95000.0},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["department"] == "DevOps"

    # Delete
    delete_resp = await client.delete(f"{EMPLOYEE_URL}{employee_id}")
    assert delete_resp.status_code == 204

    # Verify deleted
    final_resp = await client.get(f"{EMPLOYEE_URL}{employee_id}")
    assert final_resp.status_code == 404