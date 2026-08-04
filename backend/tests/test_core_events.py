import pytest
import asyncio
from app.core.events import EventPublisher, DomainEvent

class DummyEvent(DomainEvent):
    user_id: int
    action: str

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    bus = EventPublisher()
    
    # Store received events here
    received_events = []
    
    async def dummy_handler(event: DummyEvent):
        received_events.append(event)
        
    # Subscribe handler
    bus.subscribe(DummyEvent, dummy_handler)
    
    # Publish event
    test_event = DummyEvent(user_id=1, action="test_action")
    await bus.publish(test_event)
    
    # Wait for fire-and-forget tasks to complete
    await asyncio.sleep(0.1)
    
    # Assert event was received
    assert len(received_events) == 1
    assert received_events[0].user_id == 1
    assert received_events[0].action == "test_action"

@pytest.mark.asyncio
async def test_event_bus_multiple_handlers():
    bus = EventPublisher()
    
    counter = {"count": 0}
    
    async def handler1(event: DummyEvent):
        counter["count"] += 1
        
    async def handler2(event: DummyEvent):
        counter["count"] += 1
        
    bus.subscribe(DummyEvent, handler1)
    bus.subscribe(DummyEvent, handler2)
    
    await bus.publish(DummyEvent(user_id=2, action="multi"))
    
    # Wait for fire-and-forget tasks to complete
    await asyncio.sleep(0.1)
    
    # Both handlers should be executed
    assert counter["count"] == 2
