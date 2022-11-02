from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
