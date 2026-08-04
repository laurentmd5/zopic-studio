from datetime import datetime
import pytest
from unittest.mock import patch, AsyncMock
from app.modules.payments.events import PaymentCompletedEvent
from app.modules.athletes.handlers import update_athlete_statistics
from app.modules.athletes.models import AthleteStatistics
from app.modules.payments.models import Order, OrderItem
from app.modules.competitions.models import Photo, Epreuve, Competition

@pytest.mark.asyncio
async def test_update_athlete_statistics_guest():
    # User ID is None, should return early
    event = PaymentCompletedEvent(order_id=999, user_id=None)
    # Should not raise any exception
    await update_athlete_statistics(event)

@pytest.mark.asyncio
@patch("app.modules.athletes.handlers.AsyncSessionLocal")
async def test_update_athlete_statistics_no_items(mock_session_maker, db_session):
    # Setup mock session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = db_session
    mock_session_maker.return_value = mock_session
    
    event = PaymentCompletedEvent(order_id=998, user_id=1)
    await update_athlete_statistics(event)
    # Shouldn't fail, just returns

@pytest.mark.asyncio
@patch("app.modules.athletes.handlers.AsyncSessionLocal")
async def test_update_athlete_statistics_new_stats(mock_session_maker, db_session):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = db_session
    mock_session_maker.return_value = mock_session
    
    # Prepare data
    comp = Competition(id=1, name="Test", date=datetime(2025, 1, 1), photographer_id=1, settings={"sport": "Tennis"})
    ep = Epreuve(id=1, name="Ep1", competition_id=1)
    p1 = Photo(id=1, epreuve_id=1, s3_object_key="key1.jpg")
    p2 = Photo(id=2, epreuve_id=1, s3_object_key="key2.jpg")
    o = Order(id=100, user_id=2, total_amount=1000)
    oi1 = OrderItem(order_id=100, photo_id=1, price=1000)
    oi2 = OrderItem(order_id=100, photo_id=2, price=1000)
    
    db_session.add_all([comp, ep, p1, p2, o, oi1, oi2])
    await db_session.commit()
    
    event = PaymentCompletedEvent(order_id=100, user_id=2)
    await update_athlete_statistics(event)
    
    # Verify new stats created
    from sqlalchemy.future import select
    res = await db_session.execute(select(AthleteStatistics).filter(AthleteStatistics.user_id == 2))
    stats = res.scalar_one()
    
    assert stats.photos == 2
    assert stats.competitions == 1
    assert stats.disciplines == 1

@pytest.mark.asyncio
@patch("app.modules.athletes.handlers.AsyncSessionLocal")
async def test_update_athlete_statistics_existing_stats(mock_session_maker, db_session):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = db_session
    mock_session_maker.return_value = mock_session
    
    # Prepare existing stats
    existing_stats = AthleteStatistics(user_id=3, photos=10, competitions=2, disciplines=1)
    db_session.add(existing_stats)
    
    comp = Competition(id=2, name="Test2", date=datetime(2025, 1, 1), photographer_id=1, settings={"sport": "Natation"})
    ep = Epreuve(id=2, name="Ep2", competition_id=2)
    p1 = Photo(id=3, epreuve_id=2, s3_object_key="key3.jpg")
    o = Order(id=101, user_id=3, total_amount=1000)
    oi1 = OrderItem(order_id=101, photo_id=3, price=1000)
    
    db_session.add_all([comp, ep, p1, o, oi1])
    await db_session.commit()
    
    event = PaymentCompletedEvent(order_id=101, user_id=3)
    await update_athlete_statistics(event)
    
    # Verify stats updated
    await db_session.refresh(existing_stats)
    
    assert existing_stats.photos == 11
    assert existing_stats.competitions == 3
    assert existing_stats.disciplines == 2
