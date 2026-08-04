from app.core.events import DomainEvent

class PaymentCompletedEvent(DomainEvent):
    order_id: int
    session_id: str | None = None
    user_id: int | None = None
