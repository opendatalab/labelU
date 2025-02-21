from datetime import timedelta
from typing import List, Tuple

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.common.security import AccessToken
from labelu.internal.common.security import verify_password
from labelu.internal.common.security import get_password_hash
from labelu.internal.common.security import create_access_token
from labelu.internal.application.command.user import LoginCommand
from labelu.internal.application.command.user import SignupCommand
from labelu.internal.application.response.user import UserResponse
from labelu.internal.application.response.user import LoginResponse


async def signup(db: Session, cmd: SignupCommand) -> UserResponse:
    # check user alredy exists
    user = crud_user.get_user_by_username(db, username=cmd.username)
    if user:
        logger.error("user already exist:{}", cmd.username)
        raise LabelUException(
            code=ErrorCode.CODE_40001_USERNAME_ALREADY_EXISTS,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # new a user
    with db.begin():
        user = crud_user.create(
            db,
            User(
                username=cmd.username,
                hashed_password=get_password_hash(cmd.password),
            ),
        )

    # response
    return UserResponse(id=user.id, username=user.username)

async def list_by(db: Session, page: int, size: int, username: str = None) -> Tuple[List[UserResponse], int]:
    # get all users
    users, total = crud_user.list_by(db, page, size, username)

    # response
    return [
        UserResponse(id=user.id, username=user.username)
        for user in users
    ], total

async def login(db: Session, cmd: LoginCommand) -> LoginResponse:

    # check user exsit and verify password
    user = crud_user.get_user_by_username(db, cmd.username)
    if not user or not verify_password(cmd.password, user.hashed_password):
        raise LabelUException(
            code=ErrorCode.CODE_40000_USERNAME_OR_PASSWORD_INCORRECT,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # create access token
    access_token_expires = timedelta(minutes=settings.TOKEN_ACCESS_EXPIRE_MINUTES)
    access_token = create_access_token(
        token=AccessToken(id=user.id, username=user.username),
        expires_delta=access_token_expires,
    )

    # response
    return LoginResponse(token=f"{settings.TOKEN_TYPE} {access_token}")
