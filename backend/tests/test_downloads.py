import pytest
from app.modules.payments.events import PaymentCompletedEvent
from app.modules.downloads.handlers import handle_payment_completed
from app.modules.downloads.models import DownloadPermission
from app.modules.audit.models import AuditLog
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_handle_payment_completed(db_session, monkeypatch):
    # Mock AsyncSessionLocal used inside handler to use db_session
    class MockAsyncSessionLocal:
        async def __aenter__(self):
            return db_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    monkeypatch.setattr('app.modules.downloads.handlers.AsyncSessionLocal', MockAsyncSessionLocal)
    
    event = PaymentCompletedEvent(
        order_id=999,
        session_id="guest_123",
        user_id=None
    )
    
    await handle_payment_completed(event)
    
    # Assert DownloadPermission created
    res = await db_session.execute(select(DownloadPermission).where(DownloadPermission.order_id == 999))
    permission = res.scalars().first()
    assert permission is not None
    
    # Assert AuditLog created
    res_audit = await db_session.execute(select(AuditLog).where(AuditLog.entity_id == "999"))
    audit = res_audit.scalars().first()
    
    assert audit is not None
    assert audit.actor_type == "guest"
    assert audit.actor_id == "guest_123"
    assert audit.action == "payment_completed"
