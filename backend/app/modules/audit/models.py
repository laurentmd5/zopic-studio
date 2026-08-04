from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Actor performing the action (e.g., 'guest', 'user', 'system')
    actor_type = Column(String, nullable=False, index=True)
    # ID of the actor (e.g., user_id or session_id)
    actor_id = Column(String, nullable=False, index=True)
    
    # Entity being acted upon (e.g., 'order', 'archive', 'download_permission')
    entity_type = Column(String, nullable=False, index=True)
    # ID of the entity
    entity_id = Column(String, nullable=False, index=True)
    
    # The action performed (e.g., 'download', 'payment_completed', 'archive_created')
    action = Column(String, nullable=False, index=True)
    
    # Flexible metadata (e.g., IPs, user agents, extra context)
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
