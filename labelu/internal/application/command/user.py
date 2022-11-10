from pydantic import BaseModel, EmailStr, Field


class SignupCommand(BaseModel):
    username: EmailStr
    password: str = Field(min_length=6, max_length=18)


class LoginCommand(BaseModel):
    username: EmailStr
    password: str = Field(min_length=6, max_length=18)
