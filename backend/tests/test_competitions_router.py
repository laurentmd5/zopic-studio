import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_create_competition(async_client, db_session):
    user = User(phone_number="+221770000000", is_photographer=True)
    db_session.add(user)
    await db_session.commit()

    payload = {
        "name": "Super Event",
        "date": "2024-01-01T00:00:00Z",
        "is_public": True,
        "settings": {"price_xof": 1500}
    }
    
    mock_resp = {
        "id": 1,
        "name": "Super Event",
        "date": "2024-01-01T00:00:00Z",
        "is_public": True,
        "settings": {"price_xof": 1500},
        "photographer_id": user.id,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    with patch("app.modules.competitions.service.create_competition", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_resp
        from app.main import app
        from app.modules.auth.service import get_current_user
        app.dependency_overrides[get_current_user] = lambda: user
        
        response = await async_client.post("/competitions/", json=payload)
        
        assert response.status_code == 200
        assert response.json()["name"] == "Super Event"
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_competition(async_client):
    from app.modules.competitions.models import Competition
    from datetime import datetime
    mock_resp = Competition(
        id=1,
        name="Existing Event",
        date=datetime.now(),
        is_public=True,
        photographer_id=1,
        packs_enabled=False,
        created_at=datetime.now()
    )
    with patch("app.modules.competitions.service.get_competition", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_resp
        response = await async_client.get("/competitions/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Existing Event"

@pytest.mark.asyncio
async def test_list_competitions(async_client):
    from app.modules.competitions.models import Competition
    from datetime import datetime
    mock_resp = [Competition(
        id=1,
        name="List 1",
        date=datetime.now(),
        is_public=True,
        photographer_id=1,
        packs_enabled=False,
        created_at=datetime.now()
    )]
    with patch("app.modules.competitions.service.get_competitions", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_resp
        response = await async_client.get("/competitions/")
        assert response.status_code == 200
        assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_create_epreuve(async_client, db_session):
    user = User(phone_number="+221770000000", is_photographer=True)
    db_session.add(user)
    await db_session.commit()
    
    from app.modules.competitions.models import Competition, Epreuve
    from datetime import datetime
    comp = Competition(name="Test Comp", date=datetime.now(), photographer_id=user.id)
    db_session.add(comp)
    await db_session.commit()
    
    payload = {"name": "Course A"}
    from app.modules.competitions.models import Epreuve
    mock_resp = Epreuve(
        id=1,
        name="Course A",
        competition_id=1,
        created_at=datetime.now()
    )
    
    with patch("app.modules.competitions.service.create_epreuve", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_resp
        from app.main import app
        from app.modules.auth.service import get_current_user
        app.dependency_overrides[get_current_user] = lambda: user
        
        response = await async_client.post(f"/competitions/{comp.id}/epreuves", json=payload)
        
        assert response.status_code == 200
        assert response.json()["name"] == "Course A"
        app.dependency_overrides.clear()
