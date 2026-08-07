import pytest
from httpx import AsyncClient, RequestError, Response
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_search_faces_ai_error(async_client):
    file_content = b"fake_image_data"
    
    mock_client = AsyncMock()
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_client.post.return_value = mock_response
    
    mock_client_class = MagicMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    with patch("app.modules.face_recognition.router.httpx.AsyncClient", mock_client_class):
        response = await async_client.post(
            "/api/v1/faces/search",
            data={"competition_id": 1, "consent": True},
            files={"file": ("test.jpg", file_content, "image/jpeg")}
        )
        assert response.status_code == 500
        assert "Internal Server Error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_search_faces_network_error(async_client):
    file_content = b"fake_image_data"
    
    mock_client = AsyncMock()
    mock_client.post.side_effect = RequestError("Connection refused", request=MagicMock())
    
    mock_client_class = MagicMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    with patch("app.modules.face_recognition.router.httpx.AsyncClient", mock_client_class):
        response = await async_client.post(
            "/api/v1/faces/search",
            data={"competition_id": 1, "consent": True},
            files={"file": ("test.jpg", file_content, "image/jpeg")}
        )
        assert response.status_code == 503
        assert "AI service unavailable" in response.json()["detail"]
