from httpx import AsyncClient

ORDER_URL = "/api/orders/"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

SAMPLE_ORDER = {
    "product_name": "Wireless Mouse",
    "quantity": 2,
    "unit_price": 29.99,
}


# ── Helpers ───────────────────────────────────────────────────────────────────


async def create_order(client: AsyncClient, data: dict = None) -> dict:
    payload = data or SAMPLE_ORDER
    response = await client.post(ORDER_URL, json=payload)
    assert response.status_code == 201
    return response.json()


# ── Auth guard ────────────────────────────────────────────────────────────────


async def test_unauthenticated_cannot_list_orders(client: AsyncClient):
    response = await client.get(ORDER_URL)
    assert response.status_code == 401


async def test_unauthenticated_cannot_create_order(client: AsyncClient):
    response = await client.post(ORDER_URL, json=SAMPLE_ORDER)
    assert response.status_code == 401


async def test_invalid_token_rejected(client: AsyncClient):
    client.headers.update({"Authorization": "Bearer invalid.token.here"})
    response = await client.get(ORDER_URL)
    assert response.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────


async def test_create_order_success(auth_client: AsyncClient):
    response = await auth_client.post(ORDER_URL, json=SAMPLE_ORDER)
    assert response.status_code == 201
    data = response.json()
    assert data["product_name"] == "Wireless Mouse"
    assert data["quantity"] == 2
    assert data["unit_price"] == 29.99
    assert data["status"] == "pending"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


async def test_create_order_missing_fields(auth_client: AsyncClient):
    response = await auth_client.post(ORDER_URL, json={"product_name": "Mouse"})
    assert response.status_code == 422


async def test_create_order_zero_quantity(auth_client: AsyncClient):
    response = await auth_client.post(ORDER_URL, json={**SAMPLE_ORDER, "quantity": 0})
    assert response.status_code == 422


async def test_create_order_negative_quantity(auth_client: AsyncClient):
    response = await auth_client.post(ORDER_URL, json={**SAMPLE_ORDER, "quantity": -1})
    assert response.status_code == 422


async def test_create_order_zero_price(auth_client: AsyncClient):
    response = await auth_client.post(ORDER_URL, json={**SAMPLE_ORDER, "unit_price": 0})
    assert response.status_code == 422


async def test_create_order_negative_price(auth_client: AsyncClient):
    response = await auth_client.post(
        ORDER_URL, json={**SAMPLE_ORDER, "unit_price": -9.99}
    )
    assert response.status_code == 422


async def test_create_order_empty_product_name(auth_client: AsyncClient):
    response = await auth_client.post(
        ORDER_URL, json={**SAMPLE_ORDER, "product_name": ""}
    )
    assert response.status_code == 422


async def test_create_duplicate_pending_order_rejected(auth_client: AsyncClient):
    await create_order(auth_client)
    response = await auth_client.post(ORDER_URL, json=SAMPLE_ORDER)
    assert response.status_code == 409
    assert "pending" in response.json()["message"].lower()


async def test_create_same_product_after_cancellation_allowed(auth_client: AsyncClient):
    """Duplicate check is only for 'pending' orders — cancelled allows re-order."""
    order = await create_order(auth_client)
    await auth_client.put(f"{ORDER_URL}{order['id']}", json={"status": "cancelled"})
    response = await auth_client.post(ORDER_URL, json=SAMPLE_ORDER)
    assert response.status_code == 201


# ── List ──────────────────────────────────────────────────────────────────────


async def test_list_orders_empty(auth_client: AsyncClient):
    response = await auth_client.get(ORDER_URL)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_orders_returns_own_orders(auth_client: AsyncClient):
    await create_order(auth_client)
    await create_order(auth_client, {**SAMPLE_ORDER, "product_name": "Keyboard"})
    response = await auth_client.get(ORDER_URL)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ── Get by ID ─────────────────────────────────────────────────────────────────


async def test_get_order_by_id_success(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.get(f"{ORDER_URL}{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["product_name"] == "Wireless Mouse"


async def test_get_order_not_found(auth_client: AsyncClient):
    response = await auth_client.get(f"{ORDER_URL}999")
    assert response.status_code == 404
    assert "999" in response.json()["message"]


async def test_get_order_invalid_id(auth_client: AsyncClient):
    response = await auth_client.get(f"{ORDER_URL}0")
    assert response.status_code == 422


# ── Update ────────────────────────────────────────────────────────────────────


async def test_update_order_status(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.put(
        f"{ORDER_URL}{created['id']}",
        json={"status": "confirmed"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_update_order_quantity(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.put(
        f"{ORDER_URL}{created['id']}",
        json={"quantity": 5},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 5
    assert response.json()["product_name"] == "Wireless Mouse"  # unchanged


async def test_update_order_partial(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.put(
        f"{ORDER_URL}{created['id']}",
        json={"unit_price": 19.99},
    )
    assert response.status_code == 200
    assert response.json()["unit_price"] == 19.99
    assert response.json()["quantity"] == 2  # unchanged


async def test_update_order_invalid_status(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.put(
        f"{ORDER_URL}{created['id']}",
        json={"status": "flying"},
    )
    assert response.status_code == 422


async def test_update_order_not_found(auth_client: AsyncClient):
    response = await auth_client.put(f"{ORDER_URL}999", json={"status": "confirmed"})
    assert response.status_code == 404


# ── Delete ────────────────────────────────────────────────────────────────────


async def test_delete_order_success(auth_client: AsyncClient):
    created = await create_order(auth_client)
    response = await auth_client.delete(f"{ORDER_URL}{created['id']}")
    assert response.status_code == 204


async def test_delete_order_confirms_gone(auth_client: AsyncClient):
    created = await create_order(auth_client)
    await auth_client.delete(f"{ORDER_URL}{created['id']}")
    response = await auth_client.get(f"{ORDER_URL}{created['id']}")
    assert response.status_code == 404


async def test_delete_order_not_found(auth_client: AsyncClient):
    response = await auth_client.delete(f"{ORDER_URL}999")
    assert response.status_code == 404


# ── Data isolation ────────────────────────────────────────────────────────────


async def test_user_cannot_see_other_users_orders(client: AsyncClient):
    # User A registers, logs in, places an order
    await client.post(
        REGISTER_URL, json={"email": "a@example.com", "password": "Pass@123"}
    )
    resp_a = await client.post(
        LOGIN_URL, data={"username": "a@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_a.json()['access_token']}"})
    await client.post(ORDER_URL, json=SAMPLE_ORDER)

    # User B registers, logs in — should see zero orders
    await client.post(
        REGISTER_URL, json={"email": "b@example.com", "password": "Pass@123"}
    )
    resp_b = await client.post(
        LOGIN_URL, data={"username": "b@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_b.json()['access_token']}"})

    response = await client.get(ORDER_URL)
    assert response.status_code == 200
    assert len(response.json()) == 0


async def test_user_cannot_access_other_users_order_by_id(client: AsyncClient):
    # User A places an order
    await client.post(
        REGISTER_URL, json={"email": "a2@example.com", "password": "Pass@123"}
    )
    resp_a = await client.post(
        LOGIN_URL, data={"username": "a2@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_a.json()['access_token']}"})
    order = (await client.post(ORDER_URL, json=SAMPLE_ORDER)).json()

    # User B tries to fetch User A's order by ID
    await client.post(
        REGISTER_URL, json={"email": "b2@example.com", "password": "Pass@123"}
    )
    resp_b = await client.post(
        LOGIN_URL, data={"username": "b2@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_b.json()['access_token']}"})

    response = await client.get(f"{ORDER_URL}{order['id']}")
    assert response.status_code == 404


async def test_user_cannot_delete_other_users_order(client: AsyncClient):
    # User A places an order
    await client.post(
        REGISTER_URL, json={"email": "a3@example.com", "password": "Pass@123"}
    )
    resp_a = await client.post(
        LOGIN_URL, data={"username": "a3@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_a.json()['access_token']}"})
    order = (await client.post(ORDER_URL, json=SAMPLE_ORDER)).json()

    # User B tries to delete User A's order
    await client.post(
        REGISTER_URL, json={"email": "b3@example.com", "password": "Pass@123"}
    )
    resp_b = await client.post(
        LOGIN_URL, data={"username": "b3@example.com", "password": "Pass@123"}
    )
    client.headers.update({"Authorization": f"Bearer {resp_b.json()['access_token']}"})

    response = await client.delete(f"{ORDER_URL}{order['id']}")
    assert response.status_code == 404


# ── Full lifecycle ────────────────────────────────────────────────────────────


async def test_order_full_lifecycle(auth_client: AsyncClient):
    # Create
    created = await create_order(auth_client)
    order_id = created["id"]
    assert created["status"] == "pending"

    # Read
    get_resp = await auth_client.get(f"{ORDER_URL}{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["product_name"] == "Wireless Mouse"

    # Update status → confirmed
    upd_resp = await auth_client.put(
        f"{ORDER_URL}{order_id}", json={"status": "confirmed"}
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["status"] == "confirmed"

    # Update status → shipped
    upd_resp2 = await auth_client.put(
        f"{ORDER_URL}{order_id}", json={"status": "shipped"}
    )
    assert upd_resp2.status_code == 200
    assert upd_resp2.json()["status"] == "shipped"

    # Delete
    del_resp = await auth_client.delete(f"{ORDER_URL}{order_id}")
    assert del_resp.status_code == 204

    # Verify deleted
    final_resp = await auth_client.get(f"{ORDER_URL}{order_id}")
    assert final_resp.status_code == 404
