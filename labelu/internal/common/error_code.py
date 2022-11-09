from enum import Enum

from fastapi.responses import JSONResponse
from fastapi import Request, status, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

USER_INIT_CODE = 40000


class ErrorCode(Enum):
    """
    business error code
    """

    CODE_40000_USERNAME_OR_PASSWORD_INCORRECT = (
        USER_INIT_CODE,
        "Incorrect username or password",
    )
    CODE_40001_USERNAME_ALREADY_EXISTS = (
        USER_INIT_CODE + 1,
        "Username Aready exists in the system",
    )
    CODE_40002_USER_NOT_FOUND = (USER_INIT_CODE + 2, "User not found")
    CODE_40003_CREDENTIAL_ERROR = (USER_INIT_CODE + 3, "Could not validate credentials")
    CODE_40004_NOT_AUTHENTICATED = (USER_INIT_CODE + 4, "Not authenticated")

    CODE_50000_INTERNAL_ERROR = (50000, "Internal Error")


class UnicornException(HTTPException):
    def __init__(
        self, code: ErrorCode, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.msg = code.value[1]
        self.code = code.value[0]
        self.status_code = status_code


async def unicorn_exception_handler(request: Request, exc: UnicornException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"msg": exc.msg, "err_code": exc.code},
    )


# only for HTTPAuthorizationCredentials
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "msg": str(exc.detail),
            "err_code": ErrorCode.CODE_40004_NOT_AUTHENTICATED.value[0],
        },
    )


def exception_handlers(app):
    app.add_exception_handler(UnicornException, unicorn_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
