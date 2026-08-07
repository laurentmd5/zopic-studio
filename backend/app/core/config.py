from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ZoPic Studio"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = []
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DATABASE_URL: str
    REDIS_URL: str
    
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str = "us-east-1"
    
    QDRANT_URL: str
    
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str
    
    PAYMENT_SIMULATION_MODE: bool = False
    PAYMENT_WEBHOOK_SECRET: str = "test_webhook_secret"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @model_validator(mode='after')
    def validate_payment_secret(self) -> 'Settings':
        if not self.PAYMENT_SIMULATION_MODE and self.PAYMENT_WEBHOOK_SECRET == "test_webhook_secret":
            raise ValueError("Le secret webhook de test ne peut pas être utilisé en mode production.")
        return self

settings = Settings()
