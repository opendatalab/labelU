import uvicorn
from typer import Typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from labelu.internal.common import db
from labelu.internal.adapter.routers import user
from labelu.internal.common.config import settings
from labelu.internal.application.response.error_code import exception_handlers

# create database tables
db.Base.metadata.create_all(bind=db.engine)

description = """
labelU backend.

## Users

You will be able to:

* **Signup**
* **Login**
* **Logout** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
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

exception_handlers(app)
app.include_router(user.router, prefix=settings.API_V1_STR)


app.mount("", StaticFiles(directory="./labelu/internal/static", html=True))

cli = Typer()


@cli.command()
def main(port: int = 8000):
    uvicorn.run(app=app, port=port)


if __name__ == "__main__":
    cli()
