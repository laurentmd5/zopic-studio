import asyncio
from typing import Any, Callable, Dict, List, Type
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class DomainEvent(BaseModel):
    """Base class for all domain events."""
    pass

class EventPublisher:
    """
    Abstrait la publication d'événements.
    MVP: Implémentation in-memory (EventBus). Demain: Kafka, RabbitMQ, etc.
    """
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # Fire and forget pour ne pas bloquer le thread principal
        for handler in handlers:
            try:
                # Utiliser asyncio.create_task pour un traitement asynchrone sans bloquer la requête
                asyncio.create_task(self._safe_execute(handler, event))
            except Exception as e:
                logger.error(f"Error dispatching event {event_type.__name__} to handler {handler.__name__}: {e}")

    async def _safe_execute(self, handler: Callable, event: DomainEvent):
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Error handling event {type(event).__name__}: {e}")

# Global Event Bus instance for the monolithic MVP
event_bus = EventPublisher()
