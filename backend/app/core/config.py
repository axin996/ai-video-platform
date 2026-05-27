"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Video Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_video_platform"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_video_platform"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # MinIO / S3
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ai-video-platform"
    MINIO_SECURE: bool = False

    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # CosyVoice
    COSYVOICE_BASE_URL: str = "http://localhost:9880"

    # HeyGem
    HEYGEM_BASE_URL: str = "http://localhost:8081"
    HEYGEM_MODELS_DIR: str = "/mnt/models/heygem"

    # Whisper
    WHISPER_MODEL_SIZE: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_COMPUTE_TYPE: str = "float16"

    # Playwright / Chrome
    CHROME_DEBUG_PORT: int = 9222
    CHROME_PATH: str = "/usr/bin/google-chrome"

    # Platform OAuth
    BILIBILI_CLIENT_ID: str = ""
    BILIBILI_CLIENT_SECRET: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Flower
    FLOWER_PORT: int = 5555

    # Quota defaults
    FREE_VIDEO_GENERATIONS: int = 5
    FREE_VIDEO_MINUTES: int = 30
    FREE_PUBLISH_COUNT: int = 10

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
