import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.modules.payments import service, schemas
from app.modules.payments.models import OrderStatus

@pytest.mark.asyncio
async def test_create_order():
    mock_db = AsyncMock()
    
    # Mock des rÃ©sultats de requÃªtes DB
    # 1. Photos
    mock_photo = MagicMock(id=1, epreuve_id=10)
    mock_photo_result = MagicMock()
    mock_photo_scalars = MagicMock()
    mock_photo_scalars.all.return_value = [mock_photo]
    mock_photo_result.scalars.return_value = mock_photo_scalars
    
    # 2. Epreuves
    mock_epreuve = MagicMock(id=10, competition_id=100)
    mock_epreuve_result = MagicMock()
    mock_epreuve_scalars = MagicMock()
    mock_epreuve_scalars.all.return_value = [mock_epreuve]
    mock_epreuve_result.scalars.return_value = mock_epreuve_scalars
    
    # 3. Competitions
    mock_competition = MagicMock(id=100, user_id=99, price_per_photo=1000)
    mock_competition_result = MagicMock()
    mock_competition_scalars = MagicMock()
    mock_competition_scalars.all.return_value = [mock_competition]
    mock_competition_result.scalars.return_value = mock_competition_scalars
    
    mock_db.execute.side_effect = [
        mock_photo_result, # fetch photos
        mock_epreuve_result, # fetch epreuves
        mock_competition_result  # fetch competitions
    ]
    
    order_data = schemas.OrderCreate(photo_ids=[1])
    
    with patch('app.modules.payments.paydunya_client.PayDunyaClient.create_invoice', new_callable=AsyncMock) as mock_create_invoice:
        mock_create_invoice.return_value = {
            "token": "tok_123",
            "payment_url": "http://localhost/pay"
        }
        
        async def mock_refresh(instance):
            instance.id = 1
        mock_db.refresh.side_effect = mock_refresh
        
        response = await service.create_order(mock_db, order_data, user_id=5)
        
        assert response.total_amount == 1000
        assert response.paydunya_token == "tok_123"
        mock_create_invoice.assert_awaited_once_with(
            amount=1000,
            order_id=mock_db.add.call_args_list[0][0][0].id, # L'order mockÃ©
            cancel_url=order_data.cancel_url,
            return_url=order_data.return_url
        )

@pytest.mark.asyncio
async def test_process_webhook_success():
    mock_db = AsyncMock()
    
    mock_order = MagicMock(id=1, status=OrderStatus.PENDING)
    
    mock_order_result = MagicMock()
    mock_order_scalars = MagicMock()
    mock_order_scalars.first.return_value = mock_order
    mock_order_result.scalars.return_value = mock_order_scalars
    
    mock_items_result = MagicMock()
    mock_items_scalars = MagicMock()
    mock_items_scalars.all.return_value = []
    mock_items_result.scalars.return_value = mock_items_scalars
    
    mock_db.execute.side_effect = [
        mock_order_result, # fetch order
        mock_items_result, # fetch order items
    ]
    
    result = await service.process_webhook(mock_db, "tok_123", True)
    
    assert mock_order.status == OrderStatus.PAID
    assert result["status"] == "paid_recorded_and_ledger_created"
