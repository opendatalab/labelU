from enum import Enum

from fastapi.responses import JSONResponse
from fastapi import Request, status, HTTPException


class ErrorCode(Enum):
    """
    business error code
    """

    CODE_40000_USERNAME_OR_PASSWORD_INCORRECT = (
        40000,
        "Incorrect username or password",
    )
    CODE_40001_USERNAME_ALREADY_EXISTS = (
        40001,
        "Email Aready exists in the system",
    )


class UnicornException(HTTPException):
    def __init__(
        self, code: ErrorCode, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.msg = code.value[1]
        self.detail = code.value[1]
        self.code = code.value[0]
        self.status_code = status_code


async def unicorn_exception_handler(request: Request, exc: UnicornException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"msg": exc.msg, "err_code": exc.code},
    )


def exception_handlers(app):
    app.add_exception_handler(UnicornException, unicorn_exception_handler)
