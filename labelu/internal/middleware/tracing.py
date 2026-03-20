import time

from loguru import logger
from starlette.requests import Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware


class TracingMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        scope = request.scope
        start = time.perf_counter()
        response = None
        logger.info(f"{request.method} {scope['path']} start")

        try:
            response = await call_next(request)
            return response
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)

            # uncomments for logging response body
            # response_body = [chunk async for chunk in response.body_iterator]
            # response.body_iterator = iterate_in_threadpool(iter(response_body))
            # logger.info(f"response_body={(b''.join(response_body)).decode()}")

            status_code = response.status_code if response else "error"
            logger.info(f"{request.method} {scope['path']} end status={status_code} elapsed_ms={elapsed_ms}")
