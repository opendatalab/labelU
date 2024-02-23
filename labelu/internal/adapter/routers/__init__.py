from fastapi import FastAPI

from labelu.internal.common.config import settings
from labelu.internal.adapter.routers import user
from labelu.internal.adapter.routers import task
from labelu.internal.adapter.routers import sample
from labelu.internal.adapter.routers import attachment
from labelu.internal.adapter.routers import pre_annotation


def add_router(app: FastAPI):
    app.include_router(user.router, prefix=settings.API_V1_STR)
    app.include_router(task.router, prefix=settings.API_V1_STR)
    app.include_router(attachment.router, prefix=settings.API_V1_STR)
    app.include_router(sample.router, prefix=settings.API_V1_STR)
    app.include_router(pre_annotation.router, prefix=settings.API_V1_STR)
