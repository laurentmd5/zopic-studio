import pytest
from unittest.mock import patch, AsyncMock
from httpx import Response, RequestError, Request

@pytest.mark.asyncio
async def test_search_faces_success(async_client):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(status_code=200, json={"results": [{"photo_id": 1, "score": 0.9}]}, request=Request("POST", "http://test"))
        
        response = await async_client.post(
            "/faces/search",
            files={"file": ("test.jpg", b"fake_image_content", "image/jpeg")}
        )
        
        assert response.status_code == 200
        assert response.json() == {"results": [{"photo_id": 1, "score": 0.9}]}


