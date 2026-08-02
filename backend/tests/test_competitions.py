import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.modules.competitions import service, schemas
from app.modules.competitions.models import Competition, Epreuve, PhotoStatus

@pytest.mark.asyncio
async def test_create_competition():
    # Mock de la session DB
    mock_db = AsyncMock()
    mock_competition_data = schemas.CompetitionCreate(name="Marathon", date="2026-08-01T10:00:00Z", is_public=True)
    
    competition = await service.create_competition(mock_db, mock_competition_data, user_id=1)
    
    assert competition.name == "Marathon"
    assert competition.photographer_id == 1
    assert competition.is_public == True
    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_add_photo():
    mock_db = AsyncMock()
    mock_photo = schemas.PhotoCreate(s3_object_key="originals/test.jpg")
    
    # Mock db.execute().scalars().first() for Epreuve fetch
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_epreuve = MagicMock(competition_id=5)
    mock_scalars.first.return_value = mock_epreuve
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    # On mock create_pool pour ne pas déclencher Redis
    with patch('app.modules.competitions.service.create_pool', new_callable=AsyncMock) as mock_create_pool:
        mock_redis = AsyncMock()
        mock_create_pool.return_value = mock_redis
        
        photo = await service.add_photo(mock_db, epreuve_id=10, photo_data=mock_photo)
        
        assert photo.epreuve_id == 10
        assert photo.s3_object_key == "originals/test.jpg"
        assert photo.watermark_s3_key == "watermarks/test.jpg"
        assert photo.status == PhotoStatus.UPLOADED
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

        # Vérifie que les jobs ont été mis en queue
        assert mock_redis.enqueue_job.await_count == 2
        # Verify call to generate_watermark
        mock_redis.enqueue_job.assert_any_call(
            'generate_watermark',
            photo.id,
            photo.s3_object_key,
            photo.watermark_s3_key
        )
        # Verify call to extract_faces
        mock_redis.enqueue_job.assert_any_call(
            'extract_faces',
            photo.id,
            5, # competition_id from mock_epreuve
            10, # epreuve_id
            photo.s3_object_key,
            _queue_name='arq:ai_queue'
        )
