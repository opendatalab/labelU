from fastapi import APIRouter, status, Header
from labelu.internal.application.command.user import LoginCommand, SignupCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.user import (
    LoginResponse,
    LogoutResponse,
    SignupResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/signup",
    response_model=OkResp[SignupResponse],
    status_code=status.HTTP_201_CREATED,
)
async def signup(signup_command: SignupCommand) -> OkResp[SignupResponse]:
    """
    User signup a account
    \f
    :param signup_command: User input
    """
    return OkResp[SignupResponse](data=SignupResponse(id=5, email="user@example.com"))


@router.post(
    "/login", response_model=OkResp[LoginResponse], status_code=status.HTTP_200_OK
)
async def login(login_command: LoginCommand):
    """
    User login, get an access token for future requests
    \f
    :param login_command: User input
    """
    return OkResp[LoginResponse](data=LoginResponse(token="token"))


@router.post(
    "/logout", response_model=OkResp[LogoutResponse], status_code=status.HTTP_200_OK
)
async def logout(token: str | None = Header(default=None, description="your token")):
    """
    User logout
    :header token: User input
    \f
    """
    return OkResp[LogoutResponse](data=LogoutResponse(msg="succeeded"))
