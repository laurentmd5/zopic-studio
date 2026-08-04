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
    event = PaymentCompletedEvent(order_id="order_guest", user_id=None, amount=1000, provider="paydunya")
    # Should not raise any exception
    await update_athlete_statistics(event)

@pytest.mark.asyncio
@patch("app.modules.athletes.handlers.AsyncSessionLocal")
async def test_update_athlete_statistics_no_items(mock_session_maker, db_session):
    # Setup mock session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = db_session
    mock_session_maker.return_value = mock_session
    
    event = PaymentCompletedEvent(order_id="order_empty", user_id=1, amount=1000, provider="paydunya")
    await update_athlete_statistics(event)
    # Shouldn't fail, just returns

@pytest.mark.asyncio
@patch("app.modules.athletes.handlers.AsyncSessionLocal")
async def test_update_athlete_statistics_new_stats(mock_session_maker, db_session):
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = db_session
    mock_session_maker.return_value = mock_session
    
    # Prepare data
    comp = Competition(id="comp_stat", name="Test", settings={"sport": "Tennis"})
    ep = Epreuve(id="ep_stat", competition_id="comp_stat")
    p1 = Photo(id="p1_stat", epreuve_id="ep_stat")
    p2 = Photo(id="p2_stat", epreuve_id="ep_stat")
    o = Order(id="order_stat", user_id=2)
    oi1 = OrderItem(order_id="order_stat", photo_id="p1_stat")
    oi2 = OrderItem(order_id="order_stat", photo_id="p2_stat")
    
    db_session.add_all([comp, ep, p1, p2, o, oi1, oi2])
    await db_session.commit()
    
    event = PaymentCompletedEvent(order_id="order_stat", user_id=2, amount=2000, provider="paydunya")
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
    
    comp = Competition(id="comp_stat2", name="Test2", settings={"sport": "Natation"})
    ep = Epreuve(id="ep_stat2", competition_id="comp_stat2")
    p1 = Photo(id="p3_stat", epreuve_id="ep_stat2")
    o = Order(id="order_stat2", user_id=3)
    oi1 = OrderItem(order_id="order_stat2", photo_id="p3_stat")
    
    db_session.add_all([comp, ep, p1, o, oi1])
    await db_session.commit()
    
    event = PaymentCompletedEvent(order_id="order_stat2", user_id=3, amount=1000, provider="paydunya")
    await update_athlete_statistics(event)
    
    # Verify stats updated
    await db_session.refresh(existing_stats)
    
    assert existing_stats.photos == 11
    assert existing_stats.competitions == 3
    assert existing_stats.disciplines == 2
