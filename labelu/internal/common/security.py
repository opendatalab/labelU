from typing import Union
from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

from labelu.internal.common.config import settings

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AccessToken(BaseModel):
    id: int
    username: str
    exp: Union[datetime, None] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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
