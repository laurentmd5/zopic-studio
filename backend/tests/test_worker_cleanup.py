import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from app.worker import arq_cleanup_biometrics
from app.modules.competitions.models import Competition, CompetitionStatus

@pytest.mark.asyncio
async def test_arq_cleanup_biometrics_deletes_old_archived_collections():
    # Setup mocks
    mock_db = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_sessionmaker = MagicMock(return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_db)))
    
    mock_qdrant = AsyncMock()
    mock_qdrant.collection_exists.return_value = True

    # Data
    old_date = datetime.now(timezone.utc) - timedelta(days=35)
    recent_date = datetime.now(timezone.utc) - timedelta(days=5)

    comp_old = Competition(id=1, status=CompetitionStatus.ARCHIVED, date=old_date)
    comp_recent = Competition(id=2, status=CompetitionStatus.ARCHIVED, date=recent_date)
    comp_no_date = Competition(id=3, status=CompetitionStatus.ARCHIVED, date=None)

    # Mock DB result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [comp_old, comp_recent, comp_no_date]
    mock_db.execute.return_value = mock_result

    with patch("app.worker.create_async_engine", return_value=mock_engine):
        with patch("app.worker.async_sessionmaker", return_value=mock_sessionmaker):
            with patch("app.worker.AsyncQdrantClient", return_value=mock_qdrant):
                await arq_cleanup_biometrics({})

    # Assertions
    # Should only delete collection for comp_old (id=1)
    mock_qdrant.delete_collection.assert_called_once_with("faces_v1_1")
    
    # Ensure it checked existence
    mock_qdrant.collection_exists.assert_called_once_with("faces_v1_1")

@pytest.mark.asyncio
async def test_arq_cleanup_biometrics_skips_non_existent_collections():
    # Setup mocks
    mock_db = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_sessionmaker = MagicMock(return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_db)))
    
    mock_qdrant = AsyncMock()
    mock_qdrant.collection_exists.return_value = False # Collection already deleted

    # Data
    old_date = datetime.now(timezone.utc) - timedelta(days=35)
    comp_old = Competition(id=1, status=CompetitionStatus.ARCHIVED, date=old_date)

    # Mock DB result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [comp_old]
    mock_db.execute.return_value = mock_result

    with patch("app.worker.create_async_engine", return_value=mock_engine):
        with patch("app.worker.async_sessionmaker", return_value=mock_sessionmaker):
            with patch("app.worker.AsyncQdrantClient", return_value=mock_qdrant):
                await arq_cleanup_biometrics({})

    # Assertions
    # Should check existence
    mock_qdrant.collection_exists.assert_called_once_with("faces_v1_1")
    # But should NOT delete because it does not exist
    mock_qdrant.delete_collection.assert_not_called()
