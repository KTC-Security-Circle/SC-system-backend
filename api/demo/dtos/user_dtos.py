from enum import Enum

from pydantic import EmailStr, Field, field_validator
from sqlmodel import SQLModel


class UserDTO(SQLModel):
    id: str
    name: str
    email: EmailStr
    authority: str
    major: str

    class Config:
        schema_extra = {
            "example": {
                "id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "name": "Taro Yamada",
                "email": "taro.yamada@example.com",
                "authority": "admin",
                "major": "fugafuga専攻",
            }
        }


class UserCreateDTO(SQLModel):
    name: str | None = Field(default="名無し", max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=12)
    authority: str | None = Field(default="student")
    major: str | None = Field(default="fugafuga専攻", max_length=255)


class UserOrderBy(str, Enum):
    name = "name"
    email = "email"
    authority = "authority"
    pub_data = "pub_data"
    major = "major"


class UserSearchDTO(SQLModel):
    name: str | None = None
    name_like: str | None = None
    email: EmailStr | None = None
    authority: str | None = None
    major_like: str | None = None  # 部分一致フィルタ

    @field_validator("authority")
    @classmethod
    def validate_authority(cls, value: str) -> str:
        valid_roles = ["admin", "staff", "student"]
        if value and value not in valid_roles:
            raise ValueError("Invalid role specified")
        return value


class UserUpdateDTO(SQLModel):
    name: str | None = Field(None, max_length=150)
    email: EmailStr | None
    password: str | None = Field(None, min_length=8, max_length=12)
    authority: str | None = Field(None)
    major: str | None = Field(None, max_length=255)

    @field_validator("authority")
    @classmethod
    def validate_authority(cls, value: str) -> str:
        valid_roles = ["admin", "staff", "student"]
        if value and value not in valid_roles:
            raise ValueError("Invalid role specified")
        return value
