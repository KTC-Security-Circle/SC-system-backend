from sqlmodel import SQLModel
from pydantic import EmailStr


# Tokenモデル
class Token(SQLModel):
    access_token: str
    token_type: str


# LoginDataモデル
class LoginData(SQLModel):
    email: EmailStr
    password: str