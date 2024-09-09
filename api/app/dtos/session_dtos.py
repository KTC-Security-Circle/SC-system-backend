from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional


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
                "user_id": 1
            }
        }