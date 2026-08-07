import logging
from typing import Type
from pydantic import BaseModel
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

logger = logging.getLogger(__name__)

class DomainEvent(BaseModel):
    """Base class for all domain events."""
    pass

class EventPublisher:
    """
    Publisher qui utilise Redis (ARQ) pour enqueuer les tâches persistantes.
    """
    def __init__(self):
        self._pool = None

    async def _get_pool(self):
        if not self._pool:
            self._pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        return self._pool

    async def publish(self, db, event: DomainEvent):
        event_dict = event.model_dump(mode='json')
        event_type_name = type(event).__name__
        
        from app.core.outbox import OutboxEvent
        
        try:
            outbox_evt = OutboxEvent(
                event_type=event_type_name,
                payload=event_dict,
                status="PENDING"
            )
            db.add(outbox_evt)
        except Exception as e:
            logger.error(f"Error persisting outbox event {event_type_name}: {e}")
            raise

# Global Event Bus instance
event_bus = EventPublisher()
