import os
from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from labelu.internal.common.io import get_data_dir


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    SCHEME: str = "http"
    HOST: str = "localhost"
    PORT: str = "8000"
    API_V1_STR: str = "/api/v1"
    MEDIA_HOST: str = f"{SCHEME}://{HOST}:{PORT}"

    BASE_DATA_DIR: str = get_data_dir()
    MEDIA_ROOT: Path = Path(BASE_DATA_DIR).joinpath("media")
    UPLOAD_DIR: str = "upload"
    EXPORT_DIR: str = "export"
    UPLOAD_FILE_MAX_SIZE: int = 200_000_000  # ~200MB
    THUMBNAIL_HEIGH_PIXEL: int = 120
    STORAGE_BACKEND: str = "local"

    S3_ENDPOINT: str = ""
    S3_REGION: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_PUBLIC_BASE_URL: str = ""
    S3_PRESIGN_EXPIRE_SECONDS: int = 3600
    S3_PATH_STYLE: bool = False
    S3_USE_SSL: bool = True

    AI_AUTO_LABEL_ENABLED: bool = False
    AI_PROVIDER: str = "local_http"
    AI_MODEL_ENDPOINT: str = ""
    AI_MODEL_TIMEOUT_SECONDS: int = 60
    AI_MODEL_NAME: str = ""
    AI_IMAGE_URL_EXPIRE_SECONDS: int = 300

    DATABASE_URL: str = Field(
        # default="mysql://labelu:labelupass@localhost/labeludb",
        default=f"sqlite:///{BASE_DATA_DIR}/labelu.sqlite",
        description="Database connection URL. Supports SQLite and MySQL."
    )
    # or using MySQL DATABASE_URL=mysql://labelu:labelupass@localhost/labeludb

    PASSWORD_SECRET_KEY: str = Field(
        default="",
        description="JWT secret key. Generate with: openssl rand -hex 32. MUST be set in production."
    )

    TOKEN_GENERATE_ALGORITHM: str = "HS256"
    TOKEN_ACCESS_EXPIRE_MINUTES: int = 30
    TOKEN_TYPE: str = "Bearer"
    EXPOSE_INTERNAL_ERRORS: bool = False

    @property
    def need_migration_to_mysql(self) -> bool:
        sqlite_path = Path(self.BASE_DATA_DIR) / "labelu.sqlite"
        return (
            self.DATABASE_URL.startswith('mysql') and 
            sqlite_path.exists()
        )



settings = Settings()
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
logger.info("Database and media directory: {}", settings.BASE_DATA_DIR)
