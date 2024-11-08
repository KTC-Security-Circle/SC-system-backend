from sqlmodel import SQLModel, Field, Relationship, Column
from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr, field_validator
from sqlalchemy import Unicode


class User_Demo(SQLModel, table=True):
    id: Optional[int] = Field(
        None,
        primary_key=True,
        title="ユーザーID",
        description="ユーザーを一意に識別するためのID",
    )
    name: Optional[str] = Field(
        default="名無し",
        sa_column=Column(Unicode(150)),
        title="名前",
        description="ユーザの名前",
    )
    email: EmailStr = Field(
        ...,
        sa_column=Column(Unicode(255)),
        title="メールアドレス",
        description="ユーザのメールアドレス",
    )
    password: str = Field(
        ...,
        min_length=8,
        sa_column=Column(Unicode(255)),
        title="パスワード",
        description="ユーザのパスワード",
    )
    authority: Optional[str] = Field(
        default="student",
        sa_column=Column(Unicode(30)),
        title="権限",
        description="ユーザの権限",
    )
    major: Optional[str] = Field(
        default="fugafuga専攻",
        sa_column=Column(Unicode(255)),
        title="専攻",
        description="ユーザの専攻",
    )
    pub_data: Optional[datetime] = Field(
        None, title="公開日時", description="メッセージの公開日時", index=True
    )

    sessions: List["Session_Demo"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @field_validator("authority")
    def validate_authority(cls, value):
        valid_roles = ["admin", "staff", "student"]
        if value not in valid_roles:
            raise ValueError("Invalid role specified")
        return value

    class Config:
        schema_extra = {
            "example": {
                "id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "name": "Taro Yamada",
                "email": "taro.yamada@example.com",
                "password": "password123",
                "authority": "admin",
                "major": "fugafuga専攻",
                "pub_data": "2024-06-29T12:34:56",
            }
        }


class Session_Demo(SQLModel, table=True):
    id: Optional[int] = Field(
        None,
        primary_key=True,
        title="セッションID",
        description="セッションを一意に識別するためのID",
    )
    session_name: str = Field(
        "NewSession",
        sa_column=Column(Unicode(255)),
        title="名前",
        description="セッション名",
    )
    pub_data: Optional[datetime] = Field(
        None, title="公開日時", description="セッションの公開日時"
    )
    user_id: str = Field(
        ...,
        max_length=255,
        foreign_key="user.id",
        title="ユーザID",
        description="関連するユーザのID",
    )

    chat_logs: List["ChatLog_Demo"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    user: Optional[User_Demo] = Relationship(back_populates="sessions")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "session_name": "新しいセッション",
                "pub_data": "2024-06-29T12:35:00",
                "user_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
            }
        }


class ChatLog_Demo(SQLModel, table=True):
    id: Optional[int] = Field(
        None,
        primary_key=True,
        title="チャットID",
        description="チャットを一意に識別するためのID",
    )
    message: str = Field(
        ...,
        sa_column=Column(Unicode(255), index=True),
        title="メッセージ",
        description="チャットメッセージの内容",
    )
    bot_reply: Optional[str] = Field(
        None,
        sa_column=Column(Unicode(255)),
        title="ボットの返信",
        description="ボットの返信内容",
    )
    pub_data: Optional[datetime] = Field(
        None,
        title="公開日時",
        description="メッセージの公開日時",
        index=True,  # ここでインデックスを追加する場合、Fieldの引数としてindex=Trueを指定
    )
    session_id: Optional[int] = Field(
        None,
        foreign_key="session.id",
        title="セッションID",
        description="関連するセッションのID",
    )

    session: Optional["Session_Demo"] = Relationship(back_populates="chat_logs")

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
