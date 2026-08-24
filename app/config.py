from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-pro"

    FILE_TTL_SECONDS: int = 86400  # 24h — expiração automática do PDF e do resultado no Redis

    MAX_PDF_PAGES: int = 5000
    PDF_CHUNK_SIZE: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
