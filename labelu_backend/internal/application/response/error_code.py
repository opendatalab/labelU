from enum import Enum
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse


class ErrorCode(Enum):
    """
    business error code
    """

    CODE_50000_EXAMPLE = 20000, "this is a error msg"


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
        content={"msg": exc.msg, "errorCode": exc.code},
    )


def exception_handlers(app):
    app.add_exception_handler(UnicornException, unicorn_exception_handler)
