import pytest
from unittest.mock import patch, AsyncMock
from app.modules.competitions.service import (
    create_competition, get_competitions, get_competition, create_epreuve
)
from app.modules.competitions.schemas import CompetitionCreate, EpreuveCreate
from app.modules.auth.models import User

@pytest.mark.asyncio
async def test_create_and_get_competitions(db_session):
    # Setup user
    user = User(phone_number="+221770000000", is_photographer=True)
    db_session.add(user)
    await db_session.commit()
    
    # Create competition
    comp_data = CompetitionCreate(name="Test Comp", date="2024-01-01T00:00:00Z", is_public=True)
    comp = await create_competition(db_session, comp_data, user.id)
    assert comp.name == "Test Comp"
    
    # Get all competitions
    comps = await get_competitions(db_session, limit=10, skip=0)
    assert len(comps) >= 1
    
    # Get single competition
    fetched = await get_competition(db_session, comp.id)
    assert fetched.id == comp.id

@pytest.mark.asyncio
async def test_get_competition_not_found(db_session):
    result = await get_competition(db_session, 9999)
    assert result is None

@pytest.mark.asyncio
async def test_add_epreuve(db_session):
    user = User(phone_number="+221770000001", is_photographer=True)
    db_session.add(user)
    await db_session.commit()
    
    comp_data = CompetitionCreate(name="Test Comp 2", date="2024-01-01T00:00:00Z", is_public=True)
    comp = await create_competition(db_session, comp_data, user.id)
    
    epreuve_data = EpreuveCreate(name="Epreuve 1")
    epreuve = await create_epreuve(db_session, comp.id, epreuve_data)
    assert epreuve.name == "Epreuve 1"
    assert epreuve.competition_id == comp.id
