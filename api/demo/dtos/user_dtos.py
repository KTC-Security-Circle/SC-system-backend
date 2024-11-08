from pydantic import EmailStr, Field, field_validator
from sqlmodel import SQLModel
from typing import Optional
from enum import Enum


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
                "major": "fugafuga専攻"
            }
        }


class UserCreateDTO(SQLModel):
    name: Optional[str] = Field(default="名無し", max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=12)
    authority: Optional[str] = Field(default="student")
    major: Optional[str] = Field(default="fugafuga専攻", max_length=255)


class UserOrderBy(str, Enum):
    name = "name"
    email = "email"
    authority = "authority"
    pub_data = "pub_data"
    major = "major"


class UserSearchDTO(SQLModel):
    name: Optional[str] = None
    name_like: Optional[str] = None
    email: Optional[EmailStr] = None
    authority: Optional[str] = None
    major_like: Optional[str] = None  # 部分一致フィルタ

    @field_validator('authority')
    def validate_authority(cls, value):
        valid_roles = ["admin", "staff", "student"]
        if value and value not in valid_roles:
            raise ValueError('Invalid role specified')
        return value


class UserUpdateDTO(SQLModel):
    name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr]
    password: Optional[str] = Field(None, min_length=8, max_length=12)
    authority: Optional[str] = Field(None)
    major: Optional[str] = Field(None, max_length=255)

    @field_validator('authority')
    def validate_authority(cls, value):
        valid_roles = ["admin", "staff", "student"]
        if value and value not in valid_roles:
            raise ValueError('Invalid role specified')
        return value
