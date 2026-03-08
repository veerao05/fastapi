from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"


# ── Register ──────────────────────────────────────────────────────────────────


async def test_register_success(client: AsyncClient):
    response = await client.post(
        REGISTER_URL,
        json={
            "email": "user@example.com",
            "password": "Secret@123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "Secret@123"}
    await client.post(REGISTER_URL, json=payload)
    response = await client.post(REGISTER_URL, json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        REGISTER_URL,
        json={
            "email": "not-an-email",
            "password": "Secret@123",
        },
    )
    assert response.status_code == 422


async def test_register_missing_fields(client: AsyncClient):
    response = await client.post(REGISTER_URL, json={"email": "user@example.com"})
    assert response.status_code == 422


# ── Login ─────────────────────────────────────────────────────────────────────


async def test_login_success(client: AsyncClient):
    await client.post(
        REGISTER_URL,
        json={
            "email": "login@example.com",
            "password": "Secret@123",
        },
    )
    response = await client.post(
        LOGIN_URL,
        data={
            "username": "login@example.com",
            "password": "Secret@123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        REGISTER_URL,
        json={
            "email": "login2@example.com",
            "password": "Secret@123",
        },
    )
    response = await client.post(
        LOGIN_URL,
        data={
            "username": "login2@example.com",
            "password": "WrongPassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_user_not_found(client: AsyncClient):
    response = await client.post(
        LOGIN_URL,
        data={
            "username": "ghost@example.com",
            "password": "Secret@123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


async def test_login_missing_fields(client: AsyncClient):
    response = await client.post(LOGIN_URL, data={"username": "user@example.com"})
    assert response.status_code == 422
