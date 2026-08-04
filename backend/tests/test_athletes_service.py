import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from app.modules.athletes.services import (
    get_athlete_timeline,
    get_slug_suggestions,
    create_athlete_profile,
    update_athlete_profile,
    merge_guest_orders
)
from app.modules.athletes.models import AthleteProfile
from app.modules.athletes.schemas import AthleteProfileCreate, AthleteProfileUpdate
from app.modules.payments.models import Order, OrderItem, OrderStatus
from app.modules.competitions.models import Photo, Epreuve, Competition

@pytest.mark.asyncio
async def test_get_athlete_timeline_unauthorized(db_session):
    response = await get_athlete_timeline(db_session, user_id=None, session_id=None)
    assert response.message == "Veuillez vous connecter"
    assert response.total_competitions == 0

@pytest.mark.asyncio
async def test_get_slug_suggestions(db_session):
    # Setup taken slug
    profile = AthleteProfile(user_id=1, slug="moussa")
    db_session.add(profile)
    await db_session.commit()
    
    response = await get_slug_suggestions(db_session, base_slug="moussa")
    assert "moussa" not in response.suggestions
    assert len(response.suggestions) > 0
    
    # Setup free slug
    response2 = await get_slug_suggestions(db_session, base_slug="ndiaye")
    assert response2.suggestions == ["ndiaye"]

@pytest.mark.asyncio
async def test_create_athlete_profile_success(db_session):
    profile_in = AthleteProfileCreate(slug="test_slug")
    profile = await create_athlete_profile(db_session, user_id=10, profile_in=profile_in)
    assert profile.slug == "test_slug"
    assert profile.is_activated is True

@pytest.mark.asyncio
async def test_create_athlete_profile_duplicate_user(db_session):
    profile_in = AthleteProfileCreate(slug="test_slug")
    await create_athlete_profile(db_session, user_id=11, profile_in=profile_in)
    
    # Try again
    with pytest.raises(ValueError):
        await create_athlete_profile(db_session, user_id=11, profile_in=profile_in)

@pytest.mark.asyncio
async def test_create_athlete_profile_duplicate_slug(db_session):
    profile_in = AthleteProfileCreate(slug="duplicate_slug")
    await create_athlete_profile(db_session, user_id=12, profile_in=profile_in)
    
    profile_in2 = AthleteProfileCreate(slug="duplicate_slug")
    with pytest.raises(ValueError):
        await create_athlete_profile(db_session, user_id=13, profile_in=profile_in2)

@pytest.mark.asyncio
async def test_update_athlete_profile_success(db_session):
    profile_in = AthleteProfileCreate(slug="update_slug")
    profile = await create_athlete_profile(db_session, user_id=14, profile_in=profile_in)
    
    update_in = AthleteProfileUpdate()
    updated = await update_athlete_profile(db_session, user_id=14, profile_in=update_in)
    
    assert updated.slug == "update_slug"

@pytest.mark.asyncio
async def test_update_athlete_profile_not_found(db_session):
    update_in = AthleteProfileUpdate()
    with pytest.raises(ValueError, match="Profil introuvable."):
        await update_athlete_profile(db_session, user_id=999, profile_in=update_in)

@pytest.mark.asyncio
async def test_update_athlete_profile_duplicate_slug(db_session):
    profile_in1 = AthleteProfileCreate(slug="first_slug")
    await create_athlete_profile(db_session, user_id=15, profile_in=profile_in1)
    
    profile_in2 = AthleteProfileCreate(slug="second_slug")
    await create_athlete_profile(db_session, user_id=16, profile_in=profile_in2)
    
    update_in = AthleteProfileUpdate(slug="first_slug")
    with pytest.raises(ValueError):
        await update_athlete_profile(db_session, user_id=16, profile_in=update_in)

@pytest.mark.asyncio
async def test_merge_guest_orders(db_session):
    order = Order(session_id="guest_session", total_amount=1000, status=OrderStatus.PENDING)
    db_session.add(order)
    await db_session.commit()
    
    await merge_guest_orders(db_session, user_id=20, session_id="guest_session")
    
    await db_session.refresh(order)
    assert order.user_id == 20
    assert order.session_id is None

@pytest.mark.asyncio
@patch("app.modules.athletes.services.generate_download_url", new_callable=AsyncMock)
async def test_get_athlete_timeline(mock_generate_url, db_session):
    mock_generate_url.return_value = "http://fake-url.com"
    
    comp = Competition(id=1, name="Marathon", date=datetime(2025, 1, 1), photographer_id=1, settings={"sport": "Course", "location": "Dakar"})
    epreuve = Epreuve(id=1, name="10km", competition_id=1)
    photo = Photo(id=1, epreuve_id=1, s3_object_key="key1.jpg", watermark_s3_key="key1_w.jpg")
    order = Order(id=1, user_id=100, total_amount=1000, status=OrderStatus.PAID)
    order_item = OrderItem(order_id=1, photo_id=1, price=1000)
    
    db_session.add_all([comp, epreuve, photo, order, order_item])
    await db_session.commit()
    
    response = await get_athlete_timeline(db_session, user_id=100, session_id=None)
    
    assert response.total_competitions == 1
    assert response.total_photos == 1
    assert len(response.timeline) == 1
    assert response.timeline[0].year == 2025
    assert response.timeline[0].competitions[0].sport == "Course"
    assert response.timeline[0].competitions[0].location == "Dakar"
    assert response.timeline[0].competitions[0].cover_photo_url == "http://fake-url.com"
    mock_generate_url.assert_awaited_once_with("key1.jpg")
