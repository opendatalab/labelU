from pydantic import BaseModel, EmailStr, Field

class UserResponse(BaseModel):
    id: int
    username: EmailStr


class LoginResponse(BaseModel):
    token: str = Field(..., description="description: user credential")


class LogoutResponse(BaseModel):
    msg: str
