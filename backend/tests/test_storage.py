import pytest
from unittest.mock import AsyncMock, patch
from app.modules.storage import service

@pytest.mark.asyncio
async def test_generate_upload_url():
    # Mock du s3_client
    with patch('app.modules.storage.service.s3_client.generate_presigned_url', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "https://minio.mock/upload-url"
        
        result = await service.generate_upload_url(filename="photo.jpg")
        
        assert "upload_url" in result
        assert "object_key" in result
        assert result["upload_url"] == "https://minio.mock/upload-url"
        assert result["object_key"].endswith(".jpg")
        assert result["object_key"].startswith("originals/")

@pytest.mark.asyncio
async def test_generate_watermark_url():
    with patch('app.modules.storage.service.s3_client.generate_presigned_url', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = "https://minio.mock/watermark-url"
        
        result = await service.generate_upload_url(filename="photo.jpg", is_watermark=True)
        
        assert result["upload_url"] == "https://minio.mock/watermark-url"
        assert result["object_key"].startswith("watermarks/")
