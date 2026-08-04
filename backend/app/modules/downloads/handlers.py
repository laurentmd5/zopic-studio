import logging
from datetime import datetime, timedelta, timezone
from app.core.events import event_bus
from app.modules.payments.events import PaymentCompletedEvent
from app.modules.downloads.models import DownloadPermission
from app.modules.audit.models import AuditLog
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def handle_payment_completed(event: PaymentCompletedEvent):
    """
    Crée la DownloadPermission (30 jours) et log l'audit.
    """
    logger.info(f"Handling PaymentCompletedEvent for Order {event.order_id}")
    
    async with AsyncSessionLocal() as db:
        try:
            # Créer le droit de téléchargement
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            permission = DownloadPermission(
                order_id=event.order_id,
                expires_at=expires_at
            )
            db.add(permission)
            
            # Créer l'AuditLog
            actor_type = "user" if event.user_id else "guest"
            actor_id = str(event.user_id) if event.user_id else str(event.session_id)
            
            audit = AuditLog(
                actor_type=actor_type,
                actor_id=actor_id,
                entity_type="order",
                entity_id=str(event.order_id),
                action="payment_completed",
                metadata_json={"granted_download_days": 30}
            )
            db.add(audit)
            
            await db.commit()
            logger.info(f"Successfully granted DownloadPermission for Order {event.order_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to process PaymentCompletedEvent for Order {event.order_id}: {e}")

# Register handler
event_bus.subscribe(PaymentCompletedEvent, handle_payment_completed)
