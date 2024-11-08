from datetime import datetime
from enum import Enum

from pydantic import Field
from sqlmodel import SQLModel


class SessionDTO(SQLModel):
    id: int | None
    session_name: str
    pub_data: datetime | None = None
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
    session_name: str | None = Field(default="New Session", max_length=100)
    user_id: int | None = 1
    pub_data: datetime | None = None


class SessionOrderBy(str, Enum):
    session_name = "session_name"
    pub_data = "pub_data"
    user_id = "user_id"


class SessionSearchDTO(SQLModel):
    session_name: str | None = None
    session_name_like: str | None = None
    user_id: str | None = None


class SessionUpdateDTO(SQLModel):
    session_name: str | None = Field(default="New Session", max_length=100)
    pub_data: datetime | None = None
