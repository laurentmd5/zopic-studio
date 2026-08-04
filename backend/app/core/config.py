from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ZoPic Studio"
    API_V1_STR: str = "/api/v1"
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
    
    PAYMENT_SIMULATION_MODE: bool = True
    PAYMENT_WEBHOOK_SECRET: str = "test_webhook_secret"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
