import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings

class EmailClient:
    async def send_otp(self, to_email: str, otp_code: str):
        message = EmailMessage()
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = "Votre code de connexion ZoPic Studio"
        message.set_content(f"Votre code de connexion est : {otp_code}\nCe code est valable 10 minutes.")

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=settings.SMTP_TLS,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
        )

email_client = EmailClient()
