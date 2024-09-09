from pydantic import EmailStr, Field, field_validator
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from enum import Enum


class UserDTO(SQLModel):
    id: str
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
    name: Optional[str] = Field(default="名無し", max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=12)
    authority: Optional[str] = Field(default="student")


# 検索条件用のDTO
class UserOrderBy(str, Enum):
    name = "name"
    email = "email"
    authority = "authority"
    pub_data = "pub_data"


class UserSearchDTO(SQLModel):
    name: Optional[str]
    name_like: Optional[str]  # 部分一致フィルタ
    email: Optional[EmailStr]
    authority: Optional[str]
    order_by: Optional[UserOrderBy] = None

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

    @field_validator('authority')
    def validate_authority(cls, value):
        valid_roles = ["admin", "staff", "student"]
        if value and value not in valid_roles:
            raise ValueError('Invalid role specified')
        return value