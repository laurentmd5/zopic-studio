import pytest
from httpx import AsyncClient
from app.modules.athletes.models import AthleteProfile, AthleteStatistics, PrivacyLevel

@pytest.mark.asyncio
async def test_get_public_athlete_profile_success(async_client: AsyncClient, db_session):
    # Prepare data
    profile = AthleteProfile(
        user_id=101,
        slug="john-doe",
        full_name="John Doe",
        is_activated=True,
        is_public=PrivacyLevel.PUBLIC
    )
    db_session.add(profile)
    stats = AthleteStatistics(
        user_id=101,
        competitions=10,
        photos=50,
        disciplines=2,
        albums=5,
        photographers=3,
        active_since_year=2023
    )
    db_session.add(stats)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/public/athletes/john-doe")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "john-doe"
    assert data["full_name"] == "John Doe"
    assert data["statistics"]["competitions"] == 10
    assert data["statistics"]["photos"] == 50

@pytest.mark.asyncio
async def test_get_public_athlete_profile_no_stats(async_client: AsyncClient, db_session):
    # Profile with no stats row in db
    profile = AthleteProfile(
        user_id=102,
        slug="jane-doe",
        full_name="Jane Doe",
        is_activated=True,
        is_public=PrivacyLevel.PUBLIC
    )
    db_session.add(profile)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/public/athletes/jane-doe")
    
    assert response.status_code == 200
    data = response.json()
    assert data["statistics"]["competitions"] == 0
    assert data["statistics"]["photos"] == 0

@pytest.mark.asyncio
async def test_get_public_athlete_profile_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/public/athletes/not-found-slug")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"

@pytest.mark.asyncio
async def test_get_public_athlete_profile_not_activated(async_client: AsyncClient, db_session):
    profile = AthleteProfile(
        user_id=103,
        slug="inactive-doe",
        full_name="Inactive",
        is_activated=False,
        is_public=PrivacyLevel.PUBLIC
    )
    db_session.add(profile)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/public/athletes/inactive-doe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not activated"

@pytest.mark.asyncio
async def test_get_public_athlete_profile_private(async_client: AsyncClient, db_session):
    profile = AthleteProfile(
        user_id=104,
        slug="private-doe",
        full_name="Private",
        is_activated=True,
        is_public=PrivacyLevel.PRIVATE
    )
    db_session.add(profile)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/public/athletes/private-doe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile is private"
