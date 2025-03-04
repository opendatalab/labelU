from typing import Any
from loguru import logger
import uvicorn
from typer import Typer
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from labelu.internal.adapter.routers import add_router
from labelu.internal.adapter.ws import add_ws_router
from labelu.internal.middleware import add_middleware
from labelu.internal.common.logger import init_logging
from labelu.internal.common.db import init_tables
from labelu.internal.common.config import settings
from labelu.internal.common.error_code import add_exception_handler
from labelu.alembic_labelu.run_migrate import run_db_migrations
from labelu.scripts.migrate_to_mysql import migrate_to_mysql

from .version import version as labelu_version

description = """
labelU backend.

## Users

You will be able to:

* **Signup**
* **Login**
* **Logout**.

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
    version=labelu_version,
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
run_db_migrations()
add_exception_handler(app=app)
add_router(app=app)
add_ws_router(app=app)
add_middleware(app=app)

def startup():
    if settings.need_migration_to_mysql:
        logger.info("Migrating database to MySQL")
        migrate_to_mysql()

app.add_event_handler("startup", startup)

class NoCacheStaticFiles(StaticFiles):
    def __init__(self, *args: Any, **kwargs: Any):
        self.cachecontrol = "max-age=0, no-cache, no-store, must-revalidate"
        self.pragma = "no-cache"
        self.expires = "0"
        super().__init__(*args, **kwargs)

    def file_response(self, *args: Any, **kwargs: Any) -> Response:
        resp = super().file_response(*args, **kwargs)
        
        # No cache for html files
        if resp.media_type == "text/html":
            resp.headers.setdefault("Cache-Control", self.cachecontrol)
            resp.headers.setdefault("Pragma", self.pragma)
            resp.headers.setdefault("Expires", self.expires)
            
        return resp

app.mount("", NoCacheStaticFiles(packages=["labelu.internal"], html=True))

cli = Typer()

@cli.command('migrate_to_mysql')
def to_mysql():
    """Migrate database to MySQL"""
    migrate_to_mysql()

@cli.callback(invoke_without_command=True)
def main(
    host: str = "localhost", port: int = 8000, media_host: str = "http://localhost:8000"
):
    if port:
        settings.PORT = port
    if host:
        settings.HOST = host
    if media_host:
        settings.MEDIA_HOST = media_host
        
    uvicorn.run(app=app, host=settings.HOST, port=settings.PORT, ws="websockets")
        

if __name__ == "__main__":
    cli()