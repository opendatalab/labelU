from typing import Optional
from datetime import timedelta

from jose import jwt
from loguru import logger
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, WebSocket, status, Depends, Request, Response

from labelu.internal.domain.models.user import User
from labelu.internal.common import db as db_module
from labelu.internal.common.config import settings
from labelu.internal.common.security import AccessToken
from labelu.internal.common.security import create_access_token
from labelu.internal.common.security import should_refresh_token
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.adapter.persistence import crud_user


class SpecialOAuth2PasswordBearer:
    def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization", "")
        if not authorization:
            raise LabelUException(
                code=ErrorCode.CODE_40003_CREDENTIAL_ERROR,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        _, _, param = authorization.partition(" ")
        return param


reusable_oauth2 = SpecialOAuth2PasswordBearer()


def get_current_user(
    response: Response,
    db: Session = Depends(db_module.get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.PASSWORD_SECRET_KEY,
            algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
            options={"verify_exp": True},
        )
        token_data = AccessToken(**payload)
    except (jwt.JWTError, ValidationError):
        raise LabelUException(
            code=ErrorCode.CODE_40003_CREDENTIAL_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user = crud_user.get(db, id=token_data.id)
    if not user:
        raise LabelUException(code=ErrorCode.CODE_40002_USER_NOT_FOUND, status_code=401)

    # Sliding refresh: hand back a freshly issued token (same `Bearer xxx`
    # format the login endpoint returns) when the current one is close to
    # expiry, so active users are never logged out mid-session.
    if should_refresh_token(payload.get("exp")):
        new_token = create_access_token(
            token=AccessToken(id=user.id, username=user.username),
            expires_delta=timedelta(minutes=settings.TOKEN_ACCESS_EXPIRE_MINUTES),
        )
        response.headers["X-New-Token"] = f"{settings.TOKEN_TYPE} {new_token}"

    return user


async def verify_ws_token(websocket: WebSocket, db: Session = Depends(db_module.get_db)):
    try:
        token = websocket.query_params.get('token')
        
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            raise HTTPException(status_code=401, detail="Missing authentication token")
            
        payload = jwt.decode(
            token,
            settings.PASSWORD_SECRET_KEY,
            algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
            options={"verify_exp": True},
        )

        token_data = AccessToken(**payload)
        user = crud_user.get(db, id=token_data.id)
        
        if not user:
            await websocket.close(code=4002, reason="User not found")
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except jwt.JWTError as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        await websocket.close(code=4003, reason="Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")