import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.main import app

@pytest.mark.asyncio
async def test_get_upload_url(async_client):
    user = User(id=1, phone_number="1234", is_photographer=True)
    app.dependency_overrides[get_current_user] = lambda: user
    with patch("app.modules.storage.service.generate_upload_url", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {"upload_url": "http://s3/upload", "object_key": "test.jpg"}
        
        response = await async_client.post("/api/v1/storage/upload-url", json={"filename": "test.jpg"})
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json()["upload_url"] == "http://s3/upload"

@pytest.mark.asyncio
async def test_get_upload_url_error(async_client):
    user = User(id=1, phone_number="1234", is_photographer=True)
    app.dependency_overrides[get_current_user] = lambda: user
    with patch("app.modules.storage.service.generate_upload_url", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = Exception("S3 error")
        
        response = await async_client.post("/api/v1/storage/upload-url", json={"filename": "test.jpg"})
        app.dependency_overrides.clear()
        assert response.status_code == 500
        assert "S3 error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_download_url(async_client):
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user] = lambda: user
    with patch("app.modules.storage.service.generate_download_url", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "http://s3/download"
        
        response = await async_client.get("/api/v1/storage/download-url?object_key=test.jpg")
        app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json()["download_url"] == "http://s3/download"

@pytest.mark.asyncio
async def test_get_download_url_error(async_client):
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user] = lambda: user
    with patch("app.modules.storage.service.generate_download_url", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = Exception("S3 download error")
        
        response = await async_client.get("/api/v1/storage/download-url?object_key=test.jpg")
        app.dependency_overrides.clear()
        assert response.status_code == 500
