"""
Backend Configuration

Environment-based settings for CampaignCraft AI backend.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # LLM Tiers
    GROQ_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Image Generation
    IDEOGRAM_API_KEY: str = ""

    # App URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CAMPAIGN_OUTPUTS_DIR: str = "./outputs"

    # JWT
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
