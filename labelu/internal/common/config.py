import os
from pathlib import Path

from loguru import logger
from pydantic import BaseSettings

from labelu.internal.common.io import get_data_dir


class Settings(BaseSettings):
    SCHEME: str = "http"
    HOST: str = "localhost"
    PORT: str = "8000"
    API_V1_STR: str = "/api/v1"

    BASE_DATA_DIR = get_data_dir()
    MEDIA_ROOT = Path(BASE_DATA_DIR).joinpath("media")
    UPLOAD_DIR = "upload"
    EXOIRT_DIR = "export"
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    logger.info("Database and media directory: {}", BASE_DATA_DIR)
    UPLOAD_FILE_MAX_SIZE = 200_000_000  # ~200MB
    THUMBNAIL_HEIGH_PIXEL = 120

    DATABASE_URL: str = f"sqlite:///{BASE_DATA_DIR}/labelu.sqlite"

    PASSWORD_SECRET_KEY = (
        "e5b7d00a59aaa2a5ea86a7c4d72f856b20bafa1b8d0e66124082ada81f6340bd"
    )

    TOKEN_GENERATE_ALGORITHM = "HS256"
    TOKEN_ACCESS_EXPIRE_MINUTES = 30
    TOKEN_TYPE = "Bearer"

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
