import pytest
from app.modules.payments import service, schemas
from app.modules.payments.models import OrderStatus, Order
from app.modules.competitions.models import Photo, Epreuve, Competition
from app.modules.auth.models import User
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_create_order_with_packs(db_session):
    # Setup test data
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    from datetime import datetime, timezone
    comp = Competition(
        name="Test Event", 
        date=datetime.now(timezone.utc),
        photographer_id=user.id,
        settings={"price_xof": 1500},
        packs_enabled=True,
        packs=[
            {"quantity": 5, "price_xof": 5000, "label": "5 photos"},
            {"quantity": 10, "price_xof": 8000, "label": "10 photos"}
        ]
    )
    db_session.add(comp)
    await db_session.commit()
    
    epreuve = Epreuve(name="Epreuve 1", competition_id=comp.id)
    db_session.add(epreuve)
    await db_session.commit()
    
    # Add 7 photos (Expect 1 pack of 5 = 5000 + 2 unit = 3000 -> Total 8000)
    photos = []
    for i in range(7):
        p = Photo(epreuve_id=epreuve.id, s3_object_key=f"url_{i}")
        db_session.add(p)
        photos.append(p)
    await db_session.commit()
    
    photo_ids = [p.id for p in photos]
    order_data = schemas.OrderCreate(photo_ids=photo_ids, amount_expected=8000)
    
    # Mock PayDunya
    with patch('app.modules.payments.paydunya_client.PayDunyaClient.create_invoice', new_callable=AsyncMock) as mock_invoice:
        mock_invoice.return_value = {"token": "test_tok", "payment_url": "http://test"}
        
        response = await service.create_order(db_session, order_data, user_id=None, session_id="sess_123")
        
        assert response.total_amount == 8000
        assert response.paydunya_token == "test_tok"
        
        # Verify DB Order
        from sqlalchemy.future import select
        res = await db_session.execute(select(Order).where(Order.id == response.order_id))
        order = res.scalars().first()
        
        assert order.session_id == "sess_123"
        assert order.total_amount == 8000
        assert order.status == OrderStatus.PENDING

@pytest.mark.asyncio
async def test_process_webhook_emits_event(db_session):
    # Setup Order
    order = Order(
        total_amount=1500,
        status=OrderStatus.PENDING,
        paydunya_token="webhook_tok",
        session_id="sess_456"
    )
    db_session.add(order)
    await db_session.commit()
    
    # Mock event bus
    with patch('app.modules.payments.service.event_bus.publish', new_callable=AsyncMock) as mock_publish:
        result = await service.process_webhook(db_session, "webhook_tok", is_success=True)
        
        assert result["status"] == "paid_recorded_and_ledger_created"
        
        from sqlalchemy.future import select
        res = await db_session.execute(select(Order).where(Order.id == order.id))
        updated_order = res.scalars().first()
        
        assert updated_order.status == OrderStatus.PAID
        
        # Check event emitted
        assert mock_publish.call_count == 1
        event = mock_publish.call_args[0][0]
        assert event.order_id == order.id
        assert event.session_id == "sess_456"
