from pydantic import BaseModel, EmailStr


class SignupCommand(BaseModel):
    email: EmailStr
    password: str


class LoginCommand(BaseModel):
    email: EmailStr
    password: str
