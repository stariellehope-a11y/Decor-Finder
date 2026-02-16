"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Decor Finder"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/decor_finder"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # AliExpress API
    aliexpress_app_key: str = ""
    aliexpress_app_secret: str = ""
    aliexpress_tracking_id: str = ""

    # CLIP Model
    clip_model_name: str = "ViT-B-32"
    clip_pretrained: str = "laion2b_s34b_b79k"

    # S3 / Object Storage (optional)
    s3_bucket: str = ""
    s3_endpoint: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Search
    default_search_limit: int = 24
    max_search_limit: int = 100
    embedding_dimension: int = 512  # ViT-B-32 output dim

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
