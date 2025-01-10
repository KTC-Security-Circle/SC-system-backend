import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlalchemy import Unicode, UnicodeText
from sqlmodel import Column, Field, Relationship, SQLModel

from api.app.security.role import Role


class User(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), max_length=255, primary_key=True)
    name: str | None = Field(
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
    authority: Role = Field(
        default=Role.STUDENT,
        sa_column=Column(Unicode(30)),
        title="権限",
        description="ユーザの権限",
    )
    major: str | None = Field(
        default="fugafuga専攻",
        sa_column=Column(Unicode(255)),
        title="専攻",
        description="ユーザの専攻分野",
    )
    pub_data: datetime | None = Field(None, title="公開日時", description="メッセージの公開日時", index=True)

    sessions: list["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @field_validator("authority")
    @classmethod
    def validate_authority(cls, value: str | Role) -> Role:
        try:
            # 入力値が列挙型でなければ変換を試みる
            return Role(value)
        except ValueError as e:
            raise ValueError(f"Invalid role specified: {value}. Valid roles are: {list(Role)}") from e

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


class Session(SQLModel, table=True):
    id: int | None = Field(
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
    pub_data: datetime | None = Field(None, title="公開日時", description="セッションの公開日時")
    user_id: str = Field(
        ...,
        max_length=255,
        foreign_key="user.id",
        title="ユーザID",
        description="関連するユーザのID",
    )

    chat_logs: list["ChatLog"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    user: User | None = Relationship(back_populates="sessions")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "session_name": "新しいセッション",
                "pub_data": "2024-06-29T12:35:00",
                "user_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
            }
        }


class ChatLog(SQLModel, table=True):
    id: int | None = Field(
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
    bot_reply: str | None = Field(
        None,
        sa_column=Column(Unicode(255)),
        title="ボットの返信",
        description="ボットの返信内容",
    )
    pub_data: datetime | None = Field(
        None,
        title="公開日時",
        description="メッセージの公開日時",
        index=True,  # ここでインデックスを追加する場合、Fieldの引数としてindex=Trueを指定
    )
    session_id: int | None = Field(
        None,
        foreign_key="session.id",
        title="セッションID",
        description="関連するセッションのID",
    )

    session: Optional["Session"] = Relationship(back_populates="chat_logs")

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


class SchoolInfo(SQLModel, table=True):
    id: int | None = Field(
        None,
        primary_key=True,
        title="ID",
        description="情報を一意に識別するためのID",
    )
    contents: str = Field(
        ...,
        sa_column=Column(UnicodeText),
        title="内容",
        description="学校に関する情報の内容",
    )
    pub_date: datetime | None = Field(None, title="公開日時", description="情報の公開日時", index=True)
    updated_at: datetime | None = Field(None, title="更新日時", description="情報の最終更新日時", index=True)
    created_by: str = Field(
        ...,
        foreign_key="user.id",
        title="作成者ID",
        description="情報の作成者のユーザID",
    )
    title: str | None = Field(None, sa_column=Column(UnicodeText), title="タイトル", description="学校情報のタイトル")

    creator: Optional["User"] = Relationship(back_populates="school_infos")
    groups_allowed: list["SchoolInfoGroup"] = Relationship(back_populates="schoolinfo")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "contents": "本校は2024年に設立されました。",
                "pub_date": "2024-06-29T12:34:56",
                "updated_at": "2024-07-01T09:30:00",
                "created_by": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "title": "学校の設立年",
            }
        }


class Group(SQLModel, table=True):
    id: int | None = Field(
        None,
        primary_key=True,
        title="ID",
        description="グループを一意に識別するためのID",
    )
    name: str = Field(
        ...,
        sa_column=Column(Unicode(100)),
        title="グループ名",
        description="グループの名前",
    )
    description: str | None = Field(
        None,
        sa_column=Column(Unicode(255)),
        title="説明",
        description="グループの説明",
    )

    members: list["UserGroup"] = Relationship(back_populates="group")
    schoolinfos: list["SchoolInfoGroup"] = Relationship(back_populates="group")

    class Config:
        schema_extra = {
            "example": {
                "id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "name": "Development Team",
                "description": "開発チーム",
            }
        }


class UserGroup(SQLModel, table=True):
    user_id: str = Field(
        ...,
        foreign_key="user.id",
        primary_key=True,
        title="ユーザID",
        description="関連するユーザのID",
    )
    group_id: int = Field(
        ...,
        foreign_key="group.id",
        primary_key=True,
        title="グループID",
        description="関連するグループのID",
    )

    user: Optional["User"] = Relationship(back_populates="user_groups")
    group: Optional["Group"] = Relationship(back_populates="members")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "group_id": 1,
            }
        }


class SchoolInfoGroup(SQLModel, table=True):
    schoolinfo_id: int = Field(
        ...,
        foreign_key="schoolinfo.id",
        primary_key=True,
        title="学校情報ID",
        description="関連する学校情報のID",
    )
    group_id: int = Field(
        ...,
        foreign_key="group.id",
        primary_key=True,
        title="グループID",
        description="編集権限のあるグループのID",
    )

    schoolinfo: Optional["SchoolInfo"] = Relationship(back_populates="groups_allowed")
    group: Optional["Group"] = Relationship(back_populates="schoolinfos")

    class Config:
        schema_extra = {
            "example": {
                "schoolinfo_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
                "group_id": 1,
            }
        }
