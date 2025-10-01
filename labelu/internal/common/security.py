from typing import Union
from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

from labelu.internal.common.config import settings

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password_for_bcrypt(password: str) -> str:
    """
    Truncate password to 72 bytes for bcrypt compatibility.
    
    bcrypt has a 72-byte limit. This function ensures the password
    doesn't exceed this limit while maintaining valid UTF-8 encoding.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= 72:
        return password
    
    # Truncate to 72 bytes and decode, handling incomplete UTF-8 sequences
    truncated = password_bytes[:72].decode("utf-8", errors="ignore")
    
    # Re-encode to verify it's still within limit after decode
    # (in case the decode added bytes or there were edge cases)
    while truncated and len(truncated.encode("utf-8")) > 72:
        truncated = truncated[:-1]
    
    return truncated


class AccessToken(BaseModel):
    id: int
    username: str
    exp: Union[datetime, None] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _truncate_password_for_bcrypt(plain_password[:72])
    return pwd_context.verify(safe_password, hashed_password)


def get_password_hash(password: str) -> str:
    safe_password = _truncate_password_for_bcrypt(password[:72])
    return pwd_context.hash(safe_password)


# create access token for user login
def create_access_token(
    token: AccessToken, expires_delta: Union[timedelta, None] = None
):
    # update token expire
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    token.exp = expire

    # generate jwt token
    encoded_jwt = jwt.encode(
        token.dict(),
        settings.PASSWORD_SECRET_KEY,
        algorithm=settings.TOKEN_GENERATE_ALGORITHM,
    )

    return encoded_jwt
