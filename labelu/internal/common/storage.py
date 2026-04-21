from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Optional

from PIL import Image

from labelu.internal.common.config import settings


class StorageBackend(ABC):
    @property
    @abstractmethod
    def backend_name(self) -> str:
        raise NotImplementedError

    @property
    def is_remote(self) -> bool:
        return False

    @abstractmethod
    def save_file(self, local_path: Path, key: str, content_type: Optional[str] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_bytes(self, content: bytes, key: str, content_type: Optional[str] = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read_text(self, key: str, encoding: str = "utf-8") -> str:
        raise NotImplementedError

    @abstractmethod
    def get_local_path(self, key: str) -> Optional[Path]:
        raise NotImplementedError

    @abstractmethod
    def get_read_url(self, key: str, expires_in: Optional[int] = None) -> str:
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    @property
    def backend_name(self) -> str:
        return "local"

    def _resolve(self, key: str) -> Path:
        return settings.MEDIA_ROOT.joinpath(key.lstrip("/"))

    def save_file(self, local_path: Path, key: str, content_type: Optional[str] = None) -> None:
        target_path = self._resolve(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.replace(target_path)

    def save_bytes(self, content: bytes, key: str, content_type: Optional[str] = None) -> None:
        target_path = self._resolve(key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)

    def delete(self, key: str) -> None:
        file_path = self._resolve(key)
        if file_path.exists():
            file_path.unlink()

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    def read_text(self, key: str, encoding: str = "utf-8") -> str:
        return self._resolve(key).read_text(encoding=encoding)

    def get_local_path(self, key: str) -> Optional[Path]:
        return self._resolve(key)

    def get_read_url(self, key: str, expires_in: Optional[int] = None) -> str:
        return build_absolute_media_url(build_attachment_api_path(key))


class S3StorageBackend(StorageBackend):
    def __init__(self) -> None:
        import boto3
        from botocore.config import Config

        self._bucket = settings.S3_BUCKET
        client_config = {}
        if settings.S3_REGION:
            client_config["region_name"] = settings.S3_REGION
        client_config["config"] = Config(
            s3={"addressing_style": "path" if settings.S3_PATH_STYLE else "auto"}
        )

        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT or None,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY or None,
            use_ssl=settings.S3_USE_SSL,
            **client_config,
        )

    @property
    def backend_name(self) -> str:
        return "s3"

    @property
    def is_remote(self) -> bool:
        return True

    def save_file(self, local_path: Path, key: str, content_type: Optional[str] = None) -> None:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        if extra_args:
            self._client.upload_file(str(local_path), self._bucket, key, ExtraArgs=extra_args)
        else:
            self._client.upload_file(str(local_path), self._bucket, key)

    def save_bytes(self, content: bytes, key: str, content_type: Optional[str] = None) -> None:
        kwargs = {"Bucket": self._bucket, "Key": key, "Body": content}
        if content_type:
            kwargs["ContentType"] = content_type
        self._client.put_object(**kwargs)

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except Exception:
            return False

    def read_text(self, key: str, encoding: str = "utf-8") -> str:
        result = self._client.get_object(Bucket=self._bucket, Key=key)
        return result["Body"].read().decode(encoding)

    def get_local_path(self, key: str) -> Optional[Path]:
        return None

    def get_read_url(self, key: str, expires_in: Optional[int] = None) -> str:
        expires = expires_in or settings.S3_PRESIGN_EXPIRE_SECONDS
        return self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires,
        )


def build_attachment_api_path(key: str) -> str:
    normalized = key.replace("\\", "/").lstrip("/")
    return f"{settings.API_V1_STR}/tasks/attachment/{normalized}"


def build_partial_api_path(key: str) -> str:
    normalized = key.replace("\\", "/").lstrip("/")
    return f"{settings.API_V1_STR}/tasks/partial/{normalized}"


def build_absolute_media_url(relative_url: str) -> str:
    return f"{settings.MEDIA_HOST.rstrip('/')}/{relative_url.lstrip('/')}"


def build_thumbnail_key(key: str) -> str:
    path = Path(key)
    return str(path.with_name(f"{path.stem}-thumbnail{path.suffix}")).replace("\\", "/")


def create_thumbnail_bytes(local_path: Path) -> bytes:
    image = Image.open(local_path)
    image.thumbnail(
        (
            round(image.width / image.height * settings.THUMBNAIL_HEIGH_PIXEL),
            settings.THUMBNAIL_HEIGH_PIXEL,
        ),
    )
    if image.mode != "RGB":
        image = image.convert("RGB")

    from io import BytesIO

    buffer = BytesIO()
    extension_to_format = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
    }
    format_name = extension_to_format.get(local_path.suffix.lower(), "PNG")
    image.save(buffer, format=format_name)
    return buffer.getvalue()


def get_model_read_url(key: str) -> str:
    backend = get_storage_backend()
    if backend.is_remote:
        return backend.get_read_url(key, expires_in=settings.AI_IMAGE_URL_EXPIRE_SECONDS)
    return build_absolute_media_url(build_attachment_api_path(key))


@lru_cache(maxsize=1)
def get_storage_backend() -> StorageBackend:
    if settings.STORAGE_BACKEND.lower() == "s3":
        return S3StorageBackend()
    return LocalStorageBackend()
