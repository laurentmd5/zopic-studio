import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.workers.image_tasks import generate_watermark
from app.modules.competitions.models import PhotoStatus

@pytest.mark.asyncio
@patch("app.workers.image_tasks.create_async_engine")
@patch("app.workers.image_tasks.s3_client")
@patch("app.workers.image_tasks.Image.open")
async def test_generate_watermark_success(mock_img_open, mock_s3_client, mock_engine):
    # Mock Image
    mock_img = MagicMock()
    mock_img_open.return_value = mock_img
    
    # Mock S3 Client
    mock_s3 = AsyncMock()
    
    # Mock get_object to return fake image data
    mock_body = AsyncMock()
    mock_body.read.return_value = b"fake_image_data"
    mock_s3.get_object.return_value = {'Body': mock_body}
    
    # Context manager for s3 client
    mock_s3_cm = AsyncMock()
    mock_s3_cm.__aenter__.return_value = mock_s3
    mock_s3_client.get_client.return_value = mock_s3_cm
    
    # Mock Database
    mock_db_session = AsyncMock()
    mock_db_cm = AsyncMock()
    mock_db_cm.__aenter__.return_value = mock_db_session
    
    # The async_sessionmaker returns a session context manager
    with patch("app.workers.image_tasks.async_sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value = lambda **kwargs: mock_db_cm
        
        # We also need to mock the result of scalar_one_or_none for the photographer name
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "Test Photographe"
        mock_db_session.execute.return_value = mock_result
        
        ctx = {}
        result = await generate_watermark(ctx, photo_id=1, original_key="orig.jpg", watermark_key="water.jpg")
        
        assert result is True
        mock_s3.get_object.assert_awaited_once()
        mock_s3.put_object.assert_awaited_once()
        mock_img.save.assert_called_once()
        
        # Verify db status update
        assert mock_db_session.commit.call_count >= 1

@pytest.mark.asyncio
@patch("app.workers.image_tasks.create_async_engine")
@patch("app.workers.image_tasks.s3_client")
async def test_generate_watermark_failure(mock_s3_client, mock_engine):
    # Mock S3 Client to raise an exception
    mock_s3 = AsyncMock()
    mock_s3.get_object.side_effect = Exception("S3 error")
    
    mock_s3_cm = AsyncMock()
    mock_s3_cm.__aenter__.return_value = mock_s3
    mock_s3_client.get_client.return_value = mock_s3_cm
    
    # Mock Database for error handling block
    mock_db_session = AsyncMock()
    mock_db_cm = AsyncMock()
    mock_db_cm.__aenter__.return_value = mock_db_session
    
    with patch("app.workers.image_tasks.async_sessionmaker") as mock_sessionmaker:
        mock_sessionmaker.return_value = lambda **kwargs: mock_db_cm
        
        ctx = {}
        result = await generate_watermark(ctx, photo_id=2, original_key="orig.jpg", watermark_key="water.jpg")
        
        assert result is False
        
        # Verify db status update to FAILED
        assert mock_db_session.commit.call_count == 1
