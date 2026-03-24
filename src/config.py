import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="postgresql://user:pass@localhost:5432/db")
    REDIS_URL: str = Field(default="redis://localhost:6379")
    R2_ACCOUNT_ID: str = Field(default="")
    R2_ACCESS_KEY_ID: str = Field(default="")
    R2_SECRET_ACCESS_KEY: str = Field(default="")
    R2_BUCKET_NAME: str = Field(default="dataflow")
    HYPERBOLIC_API_KEY: str = Field(default="")

    DATABASE_POOL_SIZE: int = Field(default=20)
    CHECKPOINT_DIR: str = Field(default="/data/checkpoints")
    MAX_CHART_COUNT: int = Field(default=12)
    MAX_RETRIES: int = Field(default=3)

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    return Settings()
