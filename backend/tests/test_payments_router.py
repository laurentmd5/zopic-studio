import pytest
from unittest.mock import patch, AsyncMock
from app.modules.payments.models import Order, OrderStatus
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_create_order_endpoint(async_client, db_session):
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    payload = {
        "photo_ids": [1, 2],
        "cancel_url": "http://cancel",
        "return_url": "http://return",
        "amount_expected": 2000
    }
    
    with patch("app.modules.payments.service.create_order", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"order_id": 1, "paydunya_token": "tok_123", "total_amount": 2000, "payment_url": "http://pay"}
        
        with patch("app.modules.auth.service.get_current_user_optional", return_value=user):
            response = await async_client.post("/api/v1/payments/orders", json=payload)
            assert response.status_code == 200
            assert response.json()["paydunya_token"] == "tok_123"

@pytest.mark.asyncio
async def test_simulate_webhook(async_client):
    with patch("app.modules.payments.service.process_webhook", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {"status": "paid"}
        response = await async_client.post("/api/v1/payments/simulate-webhook?token=tok_123&status=completed")
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

@pytest.mark.asyncio
async def test_get_purchases(async_client, db_session):
    order = Order(session_id="guest_1", total_amount=1500, status=OrderStatus.PAID)
    db_session.add(order)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/payments/purchases", headers={"x-session-id": "guest_1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["total_amount"] == 1500
    assert data[0]["items_count"] == 0
