from pydantic import BaseModel, EmailStr, Field


class SignupResponse(BaseModel):
    id: int
    email: EmailStr


class LoginResponse(BaseModel):
    token: str = Field(..., description="description: user credential")


class LogoutResponse(BaseModel):
    msg: str
