from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional


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