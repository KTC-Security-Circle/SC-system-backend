from pydantic import BaseModel, Field, EmailStr
from sqlmodel import Field
from datetime import datetime
from typing import Optional


class Users(BaseModel):
    id: int = Field(..., title="ユーザID", description="ユーザを一意に識別するためのID")
    name: str = Field(..., max_length=150, title="名前", description="ユーザの名前")
    email: EmailStr = Field(
        ..., title="メールアドレス", description="ユーザのメールアドレス"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=12,
        title="パスワード",
        description="ユーザのパスワード",
    )
    authority: str = Field(..., max_length=30, title="権限", description="ユーザの権限")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Taro Yamada",
                "email": "taro.yamada@example.com",
                "password": "password123",
                "authority": "admin",
            }
        }


class ChatLog(BaseModel):
    id: int = Field(
        ..., title="チャットID", description="チャットを一意に識別するためのID"
    )
    message: str = Field(
        ..., title="メッセージ", description="チャットメッセージの内容"
    )
    bot_reply: Optional[str] = Field(
        None, title="ボットの返信", description="ボットの返信内容"
    )
    pub_data: Optional[datetime] = Field(
        None, title="公開日時", description="メッセージの公開日時"
    )
    session_id: int = Field(
        ..., title="セッションID", description="関連するセッションのID"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "message": "こんにちは！",
                "bot_reply": "こんにちは！何かお手伝いできますか？",
                "pub_data": "2024-06-29T12:34:56",
                "session_id": 1,
            }
        }


class Sessions(BaseModel):
    id: int = Field(
        ..., title="セッションID", description="セッションを一意に識別するためのID"
    )
    session_name: str = Field("NewSession", title="名前", description="セッション名")
    pub_data: Optional[datetime] = Field(
        None, title="公開日時", description="セッションの公開日時"
    )
    user_id: int = Field(..., title="ユーザID", description="関連するユーザのID")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "session_name": "新しいセッション",
                "pub_data": "2024-06-29T12:35:00",
                "user_id": 1,
            }
        }


class ErrorLog(BaseModel):
    id: int = Field(
        ..., title="エラーログID", description="エラーログを一意に識別するためのID"
    )
    error_message: str = Field(
        ..., title="エラーメッセージ", description="エラーの内容"
    )
    pub_data: Optional[datetime] = Field(
        None, title="公開日時", description="エラーログの公開日時"
    )
    session_id: int = Field(
        ..., title="セッションID", description="関連するセッションのID"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "error_message": "データベース接続エラー",
                "pub_data": "2024-06-29T12:36:00",
                "session_id": 1,
            }
        }
