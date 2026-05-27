"""Shared config for workers (mirrors backend config for standalone workers)."""

import os


class Settings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_video_platform",
    )
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "ai-video-platform")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    COSYVOICE_BASE_URL: str = os.getenv("COSYVOICE_BASE_URL", "http://localhost:9880")
    HEYGEM_BASE_URL: str = os.getenv("HEYGEM_BASE_URL", "http://localhost:8081")
    HEYGEM_MODELS_DIR: str = os.getenv("HEYGEM_MODELS_DIR", "/mnt/models/heygem")

    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "large-v3")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cuda")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "float16")

    CHROME_DEBUG_PORT: int = int(os.getenv("CHROME_DEBUG_PORT", "9222"))
    CHROME_PATH: str = os.getenv("CHROME_PATH", "/usr/bin/google-chrome")

    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/ai-video-tasks")


settings = Settings()
