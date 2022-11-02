from fastapi import FastAPI
import uvicorn
from labelu.internal.adapter.routers import user
from labelu.internal.common.config import settings

description = """
labelU backend.

## Users

You will be able to:

* **Signup** (_not implemented_).
* **Login** (_not implemented_).
* **Logout** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users.",
    },
]


app = FastAPI(
    title="labelU-backend",
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

app.include_router(user.router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run(app=app)
