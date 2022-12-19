from fastapi import FastAPI

from labelu.internal.common.config import settings
from labelu.internal.middleware.tracing import TracingMiddleWare
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def add_middleware(app: FastAPI):
    app.add_middleware(TracingMiddleWare)
