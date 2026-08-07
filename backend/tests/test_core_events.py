import pytest
from unittest.mock import AsyncMock, patch
from app.core.events import EventPublisher, DomainEvent
from app.modules.payments.events import PaymentCompletedEvent

class DummyEvent(DomainEvent):
    user_id: int
    action: str

@pytest.mark.asyncio
async def test_event_bus_unmapped_event():
    bus = EventPublisher()
    
    with patch("app.core.events.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_pool = AsyncMock()
        mock_create_pool.return_value = mock_pool
        
        test_event = DummyEvent(user_id=1, action="test_action")
        mock_db = AsyncMock()
        await bus.publish(mock_db, test_event)
        
        # Should not enqueue anything since it's unmapped
        mock_pool.enqueue_job.assert_not_called()

@pytest.mark.asyncio
async def test_event_bus_payment_completed():
    bus = EventPublisher()
    
    with patch("app.core.events.create_pool", new_callable=AsyncMock) as mock_create_pool:
        mock_pool = AsyncMock()
        mock_create_pool.return_value = mock_pool
        
        test_event = PaymentCompletedEvent(order_id=1, user_id=2, session_id=None)
        mock_db = AsyncMock()
        await bus.publish(mock_db, test_event)
        
        # Should add an OutboxEvent to db
        assert mock_db.add.call_count == 1
        outbox_event = mock_db.add.call_args[0][0]
        assert outbox_event.event_type == "PaymentCompletedEvent"
        assert outbox_event.status == "PENDING"
