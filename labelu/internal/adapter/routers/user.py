from typing import Union
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Header, Depends

from labelu.internal.common import db
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.service import user as service
from labelu.internal.application.command.user import LoginCommand
from labelu.internal.application.command.user import SignupCommand
from labelu.internal.application.response.user import LoginResponse
from labelu.internal.application.response.user import LogoutResponse
from labelu.internal.application.response.user import SignupResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/signup",
    response_model=OkResp[SignupResponse],
    status_code=status.HTTP_201_CREATED,
)
async def signup(cmd: SignupCommand, db: Session = Depends(db.get_db)):
    """
    User signup a account
    """

    # business logic
    data = await service.signup(db=db, cmd=cmd)

    # response
    return OkResp[SignupResponse](data=data)


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
    token: Union[str, None] = Header(default=None, description="your token")
):
    """
    User logout
    """

    # business logic
    pass

    # response
    data = LogoutResponse(msg="succeeded")

    return OkResp[LogoutResponse](data=data)
