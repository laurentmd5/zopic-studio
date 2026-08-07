import logging

logger = logging.getLogger(__name__)

class SmsClient:
    async def send_otp(self, phone_number: str, code: str):
        # Mock SMS Client pour le MVP
        msg = f"[MOCK SMS] ZoPic Studio - Votre code OTP est: {code}"
        logger.info(f"Envoi SMS à {phone_number} : {msg}")
        print(f"\n{'='*50}\n📱 SMS POUR {phone_number}\nCODE OTP: {code}\n{'='*50}\n")
        return True

sms_client = SmsClient()
