from enum import Enum
from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from pydantic import Field

class ErrorLogDTO(SQLModel):
    id: int
    error_message: str
    pub_data: Optional[datetime] = None
    session_id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "error_message": "データベース接続エラー",
                "pub_data": "2024-06-29T12:36:00",
                "session_id": 1
            }
        }


class ErrorLogCreateDTO(SQLModel):
    error_message: str
    pub_data: Optional[datetime] = None
    session_id: Optional[int] = None


class ErrorLogOrderBy(str, Enum):
    error_message = "error_message"
    pub_data = "pub_data"
    session_id = "session_id"


class ErrorLogSearchDTO(SQLModel):
    session_id: Optional[int] = None
    error_message_like: Optional[str] = None


class ErrorLogUpdateDTO(SQLModel):
    error_message: Optional[str] = None
    pub_data: Optional[datetime] = None
    session_id: Optional[int] = None