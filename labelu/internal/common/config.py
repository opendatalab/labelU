import os
from pathlib import Path

from loguru import logger
from pydantic import BaseSettings, Field

from labelu.internal.common.io import get_data_dir


class Settings(BaseSettings):
    SCHEME: str = "http"
    HOST: str = "localhost"
    PORT: str = "8000"
    API_V1_STR: str = "/api/v1"
    MEDIA_HOST: str = f"{SCHEME}://{HOST}:{PORT}"

    BASE_DATA_DIR: str = get_data_dir()
    MEDIA_ROOT: Path = Path(BASE_DATA_DIR).joinpath("media")
    UPLOAD_DIR: str = "upload"
    EXPORT_DIR: str = "export"
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    logger.info("Database and media directory: {}", BASE_DATA_DIR)
    UPLOAD_FILE_MAX_SIZE: int = 200_000_000  # ~200MB
    THUMBNAIL_HEIGH_PIXEL: int = 120

    DATABASE_URL: str = Field(
        # default="mysql://labelu:labelupass@localhost/labeludb",
        default=f"sqlite:///{BASE_DATA_DIR}/labelu.sqlite",
        description="Database connection URL. Supports SQLite and MySQL."
    )
    # or using MySQL DATABASE_URL=mysql://labelu:labelupass@localhost/labeludb

    PASSWORD_SECRET_KEY: str = (
        "e5b7d00a59aaa2a5ea86a7c4d72f856b20bafa1b8d0e66124082ada81f6340bd"
    )

    TOKEN_GENERATE_ALGORITHM: str = "HS256"
    TOKEN_ACCESS_EXPIRE_MINUTES: int = 30
    TOKEN_TYPE: str = "Bearer"

    @property
    def need_migration_to_mysql(self) -> bool:
        sqlite_path = Path(self.BASE_DATA_DIR) / "labelu.sqlite"
        return (
            self.DATABASE_URL.startswith('mysql') and 
            sqlite_path.exists()
        )

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
