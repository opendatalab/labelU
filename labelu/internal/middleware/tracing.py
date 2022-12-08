from loguru import logger
from starlette.requests import Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware


class TracingMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        scope = request.scope
        logger.info(f"{scope['path']} start")

        response = await call_next(request)

        # uncomments for logging response body
        # response_body = [chunk async for chunk in response.body_iterator]
        # response.body_iterator = iterate_in_threadpool(iter(response_body))
        # logger.info(f"response_body={(b''.join(response_body)).decode()}")

        logger.info(f"{scope['path']} end")
        return response
