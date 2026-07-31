import uuid
from typing import Dict, Any

class PayDunyaClient:
    """
    Client PayDunya. En dÃ©veloppement, on simule l'API PayDunya.
    En production, cela utiliserait httpx pour appeler l'API de PayDunya.
    """
    
    async def create_invoice(self, amount: int, order_id: int, cancel_url: str, return_url: str) -> Dict[str, Any]:
        """
        Simule la crÃ©ation d'une facture sur PayDunya.
        Renvoie un token et une URL de paiement.
        """
        # Generation d'un token fictif unique
        token = f"tok_{uuid.uuid4().hex}"
        payment_url = f"http://localhost:8000/api/payments/simulate-payment-page?token={token}"
        
        return {
            "response_code": "00",
            "token": token,
            "response_text": "Invoice created successfully",
            "payment_url": payment_url
        }

paydunya_client = PayDunyaClient()
