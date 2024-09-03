from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from pydantic import EmailStr


class UserDTO(SQLModel):
    id: Optional[str]
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
