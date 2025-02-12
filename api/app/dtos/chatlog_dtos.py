from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel


class ChatLogDTO(SQLModel):
    id: int | None
    message: str
    bot_reply: str | None = None
    pub_data: datetime | None = None
    session_id: int
    documentid: int | None

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "message": "こんにちは！",
                "bot_reply": "こんにちは！何かお手伝いできますか？",
                "pub_data": "2024-06-29T12:34:56",
                "session_id": 1,
                "documentid": 1,
            }
        }


class ChatCreateDTO(SQLModel):
    message: str  # メッセージは必須
    bot_reply: str | None = None  # ボットの返信はオプショナル
    pub_data: datetime | None = None  # 公開日時はオプショナル
    session_id: int | None = None  # セッションIDもオプショナル

class ChatOrderBy(str, Enum):
    message = "message"
    bot_reply = "bot_reply"
    pub_data = "pub_data"
    session_id = "session_id"


class ChatSearchDTO(SQLModel):
    session_id: int | None = None
    message_like: str | None = None


class ChatUpdateDTO(SQLModel):
    message: str | None = None
    bot_reply: str | None = None
    pub_data: datetime | None = None
    session_id: int | None = None
