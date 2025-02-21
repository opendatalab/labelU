from typing import Optional

from jose import jwt
from loguru import logger
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import HTTPException, WebSocket, status, Depends, Request

from labelu.internal.domain.models.user import User
from labelu.internal.common import db
from labelu.internal.common.config import settings
from labelu.internal.common.security import AccessToken
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
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
            options={"verify_exp": False},
        )
        token_data = AccessToken(**payload)
    except (jwt.JWTError, ValidationError):
        raise LabelUException(
            code=ErrorCode.CODE_40003_CREDENTIAL_ERROR,
            status_code=status.HTTP_403_FORBIDDEN,
        )
    user = crud_user.get(db, id=token_data.id)
    if not user:
        raise LabelUException(code=ErrorCode.CODE_40002_USER_NOT_FOUND, status_code=401)
    return user


async def verify_ws_token(websocket: WebSocket, db: Session = Depends(db.get_db)):
    try:
        token = websocket.query_params.get('token')
        
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            raise HTTPException(status_code=401, detail="Missing authentication token")
            
        payload = jwt.decode(
            token,
            settings.PASSWORD_SECRET_KEY,
            algorithms=[settings.TOKEN_GENERATE_ALGORITHM],
            options={"verify_exp": False},
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