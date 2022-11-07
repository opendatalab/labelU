from pydantic import BaseModel, EmailStr, Field


class SignupCommand(BaseModel):
    username: EmailStr
    password: str


class LoginCommand(BaseModel):
    username: EmailStr
    password: str
    remember_me: bool = Field(default=False)
