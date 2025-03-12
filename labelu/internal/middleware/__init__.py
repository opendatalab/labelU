from fastapi import FastAPI

from labelu.internal.middleware.content_type import ContentTypeMiddleware
from labelu.internal.middleware.tracing import TracingMiddleWare


def add_middleware(app: FastAPI):
    app.add_middleware(TracingMiddleWare)
    app.add_middleware(ContentTypeMiddleware)
