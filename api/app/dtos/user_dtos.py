from pydantic import EmailStr
from sqlmodel import SQLModel
from typing import Optional

class UserDTO(SQLModel):
    id: Optional[str]
    name: str
    email: EmailStr
    authority: str

    class Config:
        schema_extra = {
            "example": {
                "id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "name": "Taro Yamada",
                "email": "taro.yamada@example.com",
                "authority": "admin",
            }
        }


class UserCreateDTO(SQLModel):
    name: Optional[str]
    email: EmailStr
    password: str
    authority: Optional[str]


class UserUpdate(SQLModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    authority: Optional[str]