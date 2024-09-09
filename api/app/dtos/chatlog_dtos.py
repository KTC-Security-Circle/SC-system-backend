from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional


class ChatLogDTO(SQLModel):
    id: Optional[int]
    message: str
    bot_reply: Optional[str] = None
    pub_data: Optional[datetime] = None
    session_id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "message": "こんにちは！",
                "bot_reply": "こんにちは！何かお手伝いできますか？",
                "pub_data": "2024-06-29T12:34:56",
                "session_id": 1
            }
        }