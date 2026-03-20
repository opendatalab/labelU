import asyncio
import json

from fastapi import status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import http_exception_handler
from labelu.internal.common.error_code import sqlalchemy_exception_handler
from labelu.internal.common.error_code import unexpected_exception_handler
from labelu.internal.common.error_code import validation_exception_handler


def _make_request(path: str = "/api/v1/test") -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
            "root_path": "",
        }
    )


def _json_body(response) -> dict:
    return json.loads(response.body.decode())


def test_http_exception_handler_forbidden_uses_not_authenticated_err_code():
    request = _make_request()
    exc = StarletteHTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authenticated",
    )

    response = asyncio.run(http_exception_handler(request, exc))
    data = _json_body(response)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert data["err_code"] == ErrorCode.CODE_40004_NOT_AUTHENTICATED.value[0]


def test_validation_exception_handler_returns_structured_errors():
    request = _make_request()
    exc = RequestValidationError(
        [
            {
                "loc": ("body", "username"),
                "msg": "Field required",
                "type": "missing",
                "input": {},
            }
        ]
    )

    response = asyncio.run(validation_exception_handler(request, exc))
    data = _json_body(response)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["err_code"] == ErrorCode.CODE_30002_VALIDATION_ERROR.value[0]
    assert data["msg"] == ErrorCode.CODE_30002_VALIDATION_ERROR.value[1]
    assert isinstance(data["errors"], list)
    assert data["errors"]


def test_unexpected_exception_handler_hides_internal_details_by_default():
    request = _make_request()
    original = settings.EXPOSE_INTERNAL_ERRORS
    settings.EXPOSE_INTERNAL_ERRORS = False
    try:
        response = asyncio.run(unexpected_exception_handler(request, Exception("sensitive detail")))
    finally:
        settings.EXPOSE_INTERNAL_ERRORS = original

    data = _json_body(response)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert data["err_code"] == ErrorCode.UNEXPECTED_ERROR.value[0]
    assert data["msg"] == ErrorCode.UNEXPECTED_ERROR.value[1]


def test_sqlalchemy_exception_handler_hides_internal_details_by_default():
    request = _make_request()
    original = settings.EXPOSE_INTERNAL_ERRORS
    settings.EXPOSE_INTERNAL_ERRORS = False
    try:
        response = asyncio.run(sqlalchemy_exception_handler(request, SQLAlchemyError("SELECT secret")))
    finally:
        settings.EXPOSE_INTERNAL_ERRORS = original

    data = _json_body(response)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert data["err_code"] == ErrorCode.CODE_30000_SQL_ERROR.value[0]
    assert data["msg"] == ErrorCode.CODE_30000_SQL_ERROR.value[1]
