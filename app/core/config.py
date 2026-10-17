from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://postgres:admin123@localhost:5432/nusa_db"
    SESSION_SECRET_KEY: str = "super-secret-key-change-me"
    
    AI_PROVIDER: str = "openai"
    AI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()