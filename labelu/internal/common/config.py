from pydantic import BaseSettings

from labelu.internal.common.io import get_data_dir


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./test.db"

    PASSWORD_SECRET_KEY = (
        "e5b7d00a59aaa2a5ea86a7c4d72f856b20bafa1b8d0e66124082ada81f6340bd"
    )

    TOKEN_GENERATE_ALGORITHM = "HS256"
    TOKEN_ACCESS_EXPIRE_MINUTES = 30
    TOKEN_TYPE = "Bearer"

    BASE_DATA_DIR = get_data_dir()

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
