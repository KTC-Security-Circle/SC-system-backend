from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Field


class SessionDTO(SQLModel):
    id: Optional[int]
    session_name: str
    pub_data: Optional[datetime] = None
    user_id: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "session_name": "新しいセッション",
                "pub_data": "2024-06-29T12:35:00",
                "user_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx"
            }
        }


class SessionCreateDTO(SQLModel):
    session_name: Optional[str] = Field(default="New Session", max_length=100)
    user_id: Optional[int] = 1
    pub_data: Optional[datetime] = None


class SessionOrderBy(str, Enum):
    session_name = "session_name"
    pub_data = "pub_data"
    user_id = "user_id"


class SessionSearchDTO(SQLModel):
    session_name: Optional[str] = None
    session_name_like: Optional[str] = None
    user_id: Optional[str] = None


class SessionUpdateDTO(SQLModel):
    session_name: Optional[str] = Field(default="New Session", max_length=100)
    pub_data: Optional[datetime] = None