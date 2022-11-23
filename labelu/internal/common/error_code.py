from enum import Enum

from loguru import logger
from fastapi.responses import JSONResponse
from fastapi import Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

# common init error code
COMMON_INIT_CODE = 30000

# user init error code
USER_INIT_CODE = 40000

# task init error code
TASK_INIT_CODE = 50000


class ErrorCode(Enum):
    """
    business error code
    """

    # common init error code
    CODE_30000_SQL_ERROR = (
        COMMON_INIT_CODE,
        "Excute SQL Error",
    )
    CODE_30001_NO_PERMISSION = (
        COMMON_INIT_CODE + 1,
        "Forbidden, No permission",
    )
    CODE_30002_VALIDATION_ERROR = (
        COMMON_INIT_CODE + 2,
        "validation error for request",
    )

    # user error code
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

    # task error code
    CODE_50000_TASK_ERROR = (TASK_INIT_CODE, "Internal Error")
    CODE_50001_TASK_ERROR = (TASK_INIT_CODE + 1, "Task is finished")
    CODE_50002_TASK_NOT_FOUN = (TASK_INIT_CODE + 2, "Task not found")

    # task file error code
    CODE_51000_TASK_FILE_UPLOAD_ERROR = (
        TASK_INIT_CODE + 1000,
        "Upload file error, save file failure",
    )
    CODE_51001_TASK_FILE_NOT_FOUND = (
        TASK_INIT_CODE + 1001,
        "Task file not found",
    )


class UnicornException(HTTPException):
    def __init__(
        self, code: ErrorCode, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.msg = code.value[1]
        self.code = code.value[0]
        self.status_code = status_code


async def unicorn_exception_handler(request: Request, exc: UnicornException):
    logger.error(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"msg": exc.msg, "err_code": exc.code},
    )


# only for HTTPAuthorizationCredentials
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "msg": str(exc.detail),
            "err_code": ErrorCode.CODE_40004_NOT_AUTHENTICATED.value[0],
        },
    )


# only for sqlalchemy
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "msg": str(exc),
            "err_code": ErrorCode.CODE_30000_SQL_ERROR.value[0],
        },
    )


# for http request
async def validation_exception_handler(request, exc):
    logger.error(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "msg": str(exc),
            "err_code": ErrorCode.CODE_30002_VALIDATION_ERROR.value[0],
        },
    )


def add_exception_handler(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(UnicornException, unicorn_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
