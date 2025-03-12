from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.domain.models.user import User
from labelu.internal.common.security import security
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.response.base import MetaData, OkResp, OkRespWithMeta
from labelu.internal.application.service import user as service
from labelu.internal.application.command.user import LoginCommand
from labelu.internal.application.command.user import SignupCommand
from labelu.internal.application.response.user import LoginResponse
from labelu.internal.application.response.user import LogoutResponse
from labelu.internal.application.response.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get('', response_model=OkRespWithMeta[List[UserResponse]], status_code=status.HTTP_200_OK)
async def list_users(
    authorization: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db.get_db),
    page: int | None = 0,
    size: int | None = 10,
    username: str | None = None,
):
    """
    List all users
    """

    # business logic
    data, total = await service.list_by(db=db, page=page, size=size, username=username)
    
    meta_data = MetaData(total=total, page=page, size=len(data))

    # response
    return OkRespWithMeta[List[UserResponse]](meta_data=meta_data, data=data)

@router.get('/me', response_model=OkResp[UserResponse], status_code=status.HTTP_200_OK)
async def get_me(
    authorization: HTTPAuthorizationCredentials = Security(security),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information
    """

    # response
    return OkResp[UserResponse](data=UserResponse(
        id=current_user.id,
        username=current_user.username,
    ))

@router.post(
    "/signup",
    response_model=OkResp[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def signup(cmd: SignupCommand, db: Session = Depends(db.get_db)):
    """
    User signup a account
    """

    # business logic
    data = await service.signup(db=db, cmd=cmd)

    # response
    return OkResp[UserResponse](data=data)


@router.post(
    "/login",
    response_model=OkResp[LoginResponse],
    status_code=status.HTTP_200_OK,
)
async def login(cmd: LoginCommand, db: Session = Depends(db.get_db)):
    """
    User login, get an access token for future requests
    """

    # business logic
    data = await service.login(db=db, cmd=cmd)

    # response
    return OkResp[LoginResponse](data=data)


@router.post(
    "/logout",
    response_model=OkResp[LogoutResponse],
    status_code=status.HTTP_200_OK,
)
async def logout(
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    User logout
    """

    # business logic
    pass

    # response
    data = LogoutResponse(msg="succeeded")
    return OkResp[LogoutResponse](data=data)
