import uvicorn
from typer import Typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from labelu.internal.adapter.routers import add_router
from labelu.internal.middleware import add_middleware
from labelu.internal.common.logger import init_logging
from labelu.internal.common.db import init_tables
from labelu.internal.common.config import settings
from labelu.internal.common.error_code import add_exception_handler


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
        "description": "Task manangement.",
    },
    {
        "name": "attachments",
        "description": "Task attachment management.",
    },
    {
        "name": "samples",
        "description": "Task sample manangement.",
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
add_exception_handler(app=app)
add_router(app=app)
add_middleware(app=app)

app.mount("", StaticFiles(packages=["labelu.internal"], html=True))

cli = Typer()


@cli.command()
def main(host: str = "localhost", port: int = 8000):
    if port:
        settings.PORT = port
    if host:
        settings.HOST = host
    uvicorn.run(app=app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    cli()
