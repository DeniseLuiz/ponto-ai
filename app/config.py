from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Banco de Dados
    DATABASE_URL: str

    # Redis - Mapeamento Completo para o Render
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Autenticação & Sessão
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    SESSION_EXPIRE_MINUTES: int = 480  # 8 Horas (Regula JWT + Redis)

    # Gemini & Arquivos
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-pro"
    FILE_TTL_SECONDS: int = 86400
    MAX_PDF_PAGES: int = 5000
    PDF_CHUNK_SIZE: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()