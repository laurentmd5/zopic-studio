import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import Response, Request
from datetime import datetime, timezone
from app.modules.competitions.models import Photo, Competition

@pytest.mark.asyncio
async def test_search_faces_success(async_client, db_session):
    # Mocking competition
    comp = Competition(id=1, name="Test Comp", date=datetime.now(timezone.utc), photographer_id=1, settings={"price_xof": 2000})
    db_session.add(comp)
    await db_session.commit()
    
    # Mocking photo
    photo = Photo(id=1, s3_object_key="originals/test.jpg", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()

    mock_client = AsyncMock()
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"photo_id": 1, "score": 0.9}]}
    mock_client.post.return_value = mock_response
    
    mock_client_class = MagicMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    with patch("app.modules.face_recognition.router.httpx.AsyncClient", mock_client_class):
        with patch("app.modules.face_recognition.router.s3_client.generate_presigned_url", new_callable=AsyncMock) as mock_url:
            mock_url.return_value = "http://presigned.url/test.jpg"
            
            response = await async_client.post(
                "/api/v1/faces/search",
                data={"competition_id": 1, "consent": True},
                files={"file": ("test.jpg", b"fake_image_content", "image/jpeg")}
            )
            
            assert response.status_code == 200
            json_response = response.json()
            print("JSON RESPONSE:", json_response)
            assert len(json_response["results"]) == 1
            assert json_response["results"][0]["photo_id"] == 1
            assert json_response["results"][0]["price_xof"] == 2000
            assert json_response["results"][0]["url"] == "http://presigned.url/test.jpg"
            
@pytest.mark.asyncio
async def test_forget_faces_unauthorized(async_client):
    response = await async_client.post(
        "/api/v1/faces/forget",
        data={"competition_id": 1},
        files={"file": ("test.jpg", b"fake", "image/jpeg")}
    )
    # Should require authentication
    assert response.status_code == 401
