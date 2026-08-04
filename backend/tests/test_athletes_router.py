from datetime import datetime
import unittest
import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User
from app.modules.athletes.models import AthleteProfile, AthleteStatistics

@pytest.mark.asyncio
async def test_suggest_slug(async_client):
    with patch("app.modules.athletes.router.get_slug_suggestions", new_callable=AsyncMock) as mock_service:
        mock_service.return_value = {"suggestions": ["moussa1", "moussa2"]}
        
        response = await async_client.get("/api/v1/athletes/slug-suggestions?base_slug=moussa")
        
        assert response.status_code == 200
        assert response.json() == {"suggestions": ["moussa1", "moussa2"]}
        mock_service.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_profile_success(async_client, db_session):
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    with patch("app.modules.athletes.router.create_athlete_profile", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = AthleteProfile(id=1, user_id=user.id, slug="moussa", is_public="PUBLIC", theme_color="#18181B", is_verified=False, sport_attributes={})
        
        response = await async_client.post("/api/v1/athletes/me/profile", json={
            "slug": "moussa",
            "bio": "Footballer",
            "club": "Dakar FC"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "moussa"
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_my_profile_success(async_client, db_session):
    user = User(phone_number="+221770000001")
    db_session.add(user)
    await db_session.commit()
    
    profile = AthleteProfile(user_id=user.id, slug="testslug")
    db_session.add(profile)
    stats = AthleteStatistics(user_id=user.id, competitions=5)
    db_session.add(stats)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.get("/api/v1/athletes/me/profile")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "testslug"
    assert data["statistics"]["competitions"] == 5
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_my_profile_not_found(async_client, db_session):
    user = User(phone_number="+221770000002")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.get("/api/v1/athletes/me/profile")
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_profile(async_client, db_session):
    user = User(phone_number="+221770000003")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    with patch("app.modules.athletes.router.update_athlete_profile", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = AthleteProfile(id=1, user_id=user.id, slug="updated", is_public="PUBLIC", theme_color="#18181B", is_verified=False, sport_attributes={})
        
        response = await async_client.put("/api/v1/athletes/me/profile", json={"bio": "Updated Bio"})
        
        assert response.status_code == 200
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_timeline_authenticated(async_client):
    user = User(id="user_123", phone_number="+221770000004")
    
    from app.main import app
    from app.modules.auth.service import get_current_user_optional
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    with patch("app.modules.athletes.router.get_athlete_timeline", new_callable=AsyncMock) as mock_timeline:
        mock_timeline.return_value = {"message": "Votre carriÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re sportive en images ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â ", "timeline": [], "total_competitions": 0, "total_photos": 0}
        
        response = await async_client.get("/api/v1/athletes/me/timeline")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Votre carriÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re sportive en images ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â "
        mock_timeline.assert_awaited_once_with(db=unittest.mock.ANY, user_id="user_123", session_id=None)
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_timeline_guest(async_client):
    from app.main import app
    from app.modules.auth.service import get_current_user_optional
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    with patch("app.modules.athletes.router.get_athlete_timeline", new_callable=AsyncMock) as mock_timeline:
        mock_timeline.return_value = {"message": "Le dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©but d'une grande aventure ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬", "timeline": [], "total_competitions": 0, "total_photos": 0}
        
        response = await async_client.get("/api/v1/athletes/me/timeline", headers={"X-Session-ID": "session_123"})
        
        assert response.status_code == 200
        mock_timeline.assert_awaited_once_with(db=unittest.mock.ANY, user_id=None, session_id="session_123")
        
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_timeline_unauthorized(async_client):
    from app.main import app
    from app.modules.auth.service import get_current_user_optional
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    response = await async_client.get("/api/v1/athletes/me/timeline")
    assert response.status_code == 401
    
    app.dependency_overrides.clear()
