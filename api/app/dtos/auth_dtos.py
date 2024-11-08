from pydantic import EmailStr
from sqlmodel import SQLModel


# Tokenモデル
class Token(SQLModel):
    access_token: str
    token_type: str


# LoginDataモデル
class LoginData(SQLModel):
    email: EmailStr
    password: str
