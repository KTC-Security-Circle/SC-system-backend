from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Field


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


class ChatCreateDTO(SQLModel):
    message: str  # メッセージは必須
    bot_reply: Optional[str] = None  # ボットの返信はオプショナル
    pub_data: Optional[datetime] = None  # 公開日時はオプショナル
    session_id: Optional[int] = None  # セッションIDもオプショナル


class ChatOrderBy(str, Enum):
    message = "message"
    bot_reply = "bot_reply"
    pub_data = "pub_data"
    session_id = "session_id"


class ChatSearchDTO(SQLModel):
    session_id: Optional[int] = None
    message_like: Optional[str] = None


class ChatUpdateDTO(SQLModel):
    message: Optional[str] = None
    bot_reply: Optional[str] = None
    pub_data: Optional[datetime] = None
    session_id: Optional[int] = None
