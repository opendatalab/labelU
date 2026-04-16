from typing import Union
from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import BaseModel
import bcrypt
from fastapi.security import HTTPBearer

from labelu.internal.common.config import settings

security = HTTPBearer()




class AccessToken(BaseModel):
    id: int
    username: str
    exp: Union[datetime, None] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


# create access token for user login
def create_access_token(
    token: AccessToken, expires_delta: Union[timedelta, None] = None
):
    # update token expire
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    token.exp = expire

    # generate jwt token
    encoded_jwt = jwt.encode(
        token.dict(),
        settings.PASSWORD_SECRET_KEY,
        algorithm=settings.TOKEN_GENERATE_ALGORITHM,
    )

    return encoded_jwt
