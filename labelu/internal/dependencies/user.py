from typing import Optional, Tuple

from jose import jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, status, Depends, Request

from labelu.internal.domain.models.user import User
from labelu.internal.common import db
from labelu.internal.common.config import settings
from labelu.internal.common.security import AccessToken
from labelu.internal.adapter.persistence import crud_user


class SpecialOAuth2PasswordBearer:
    def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        _, _, param = authorization.partition(" ")
        return param


reusable_oauth2 = SpecialOAuth2PasswordBearer()


def get_current_user(
    db: Session = Depends(db.get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.PASSWORD_SECRET_KEY,
            algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
        )
        token_data = AccessToken(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud_user.get_user(db, id=token_data.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
