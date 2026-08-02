import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.email_client import email_client
from app.infrastructure.qdrant_client_wrapper import qdrant_client_wrapper

@pytest.mark.asyncio
async def test_send_otp_success():
    with patch("app.infrastructure.email_client.aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        await email_client.send_otp("test@example.com", "123456")
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        message = args[0]
        assert message["To"] == "test@example.com"
        assert "123456" in message.get_content()

@pytest.mark.asyncio
async def test_qdrant_create_collection():
    with patch("app.infrastructure.qdrant_client_wrapper.qdrant_client_wrapper.client.get_collections", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(collections=[])
        with patch("app.infrastructure.qdrant_client_wrapper.qdrant_client_wrapper.client.create_collection", new_callable=AsyncMock) as mock_create:
            await qdrant_client_wrapper.create_collection_if_not_exists("test_col", 512)
            mock_create.assert_called_once()
