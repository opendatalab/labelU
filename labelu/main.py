from typing import Any
import uvicorn
from typer import Typer
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from labelu.internal.adapter.routers import add_router
from labelu.internal.middleware import add_middleware
from labelu.internal.common.logger import init_logging
from labelu.internal.common.db import init_tables
from labelu.internal.common.config import settings
from labelu.internal.common.error_code import add_exception_handler
from labelu.alembic_labelu.run_migrate import run_sqlite_migrations


description = """
labelU backend.

## Users

You will be able to:

* **Signup**
* **Login**
* **Logout** (_not implemented_).

## Tasks

You will be able to:

* **CRUD**

## Task attachment

You will be able to:

* **upload attachment**
* **download attachment**
* **delete attachment**

## Task sample

You will be able to:

* **list sample**
* **create sample**
* **get sample**
* **update sample**
* **export sample**
"""


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "tasks",
        "description": "Task management.",
    },
    {
        "name": "attachments",
        "description": "Task attachment management.",
    },
    {
        "name": "samples",
        "description": "Task sample management.",
    },
]


app = FastAPI(
    title="labelU",
    description=description,
    version="0.1.0",
    terms_of_service="",
    contact={
        "name": "labelu",
        "url": "http://labelu.example.com/contact/",
        "email": "labelu@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
)

init_logging()
init_tables()
run_sqlite_migrations()
add_exception_handler(app=app)
add_router(app=app)
add_middleware(app=app)

class NoCacheStaticFiles(StaticFiles):
    def __init__(self, *args: Any, **kwargs: Any):
        self.cachecontrol = "max-age=0, no-cache, no-store, , must-revalidate"
        self.pragma = "no-cache"
        self.expires = "0"
        super().__init__(*args, **kwargs)

    def file_response(self, *args: Any, **kwargs: Any) -> Response:
        resp = super().file_response(*args, **kwargs)
        resp.headers.setdefault("Cache-Control", self.cachecontrol)
        resp.headers.setdefault("Pragma", self.pragma)
        resp.headers.setdefault("Expires", self.expires)
        return resp

app.mount("", NoCacheStaticFiles(packages=["labelu.internal"], html=True))


@app.middleware("http")
async def add_correct_content_type(request: Request, call_next):
    response = await call_next(request)
    
    if request.url.path.endswith(".js"):
        response.headers["content-type"] = "application/javascript"
    return response


cli = Typer()


@cli.command()
def main(
    host: str = "localhost", port: int = 8000, media_host: str = "http://localhost:8000"
):
    if port:
        settings.PORT = port
    if host:
        settings.HOST = host
    if media_host:
        settings.MEDIA_HOST = media_host
    uvicorn.run(app=app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    cli()
