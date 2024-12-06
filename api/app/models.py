import uuid
from datetime import datetime
from typing import Optional, Type

from pydantic import EmailStr, field_validator
from sqlalchemy import Unicode, UnicodeText
from sqlmodel import Column, Field, Relationship, SQLModel

from api.app.security.role import Role


# ユーザ情報を定義するモデル
class User(SQLModel, table=True):
    """
    ユーザモデル: アプリケーションのユーザを表現するデータモデル。
    """

    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()),
        max_length=255,
        primary_key=True,  # 主キー
        title="ID",
        description="ユーザを一意に識別するためのID",
    )
    name: str | None = Field(
        default="名無し",
        sa_column=Column(Unicode(150)),  # 最大150文字の文字列カラム
        title="名前",
        description="ユーザの名前",
    )
    email: EmailStr = Field(
        ...,
        sa_column=Column(Unicode(255)),  # 有効なメールアドレスを必須入力
        title="メールアドレス",
        description="ユーザのメールアドレス",
    )
    password: str = Field(
        ...,
        min_length=8,  # パスワードは最低8文字
        sa_column=Column(Unicode(255)),
        title="パスワード",
        description="ユーザのパスワード",
    )
    authority: Role = Field(
        default=Role.STUDENT,  # デフォルト値を列挙型で指定
        sa_column=Column(Unicode(30)),
        title="権限",
        description="ユーザの権限",
    )
    major: str | None = Field(
        default="fugafuga専攻",
        sa_column=Column(Unicode(255)),  # 専攻の情報を保持
        title="専攻",
        description="ユーザの専攻分野",
    )
    pub_data: datetime | None = Field(
        None,
        title="公開日時",
        description="ユーザデータの公開日時",
        index=True,  # インデックスを追加
    )

    # ユーザとセッションのリレーション (1対多)
    sessions: list["Session"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},  # 子オブジェクトのカスケード削除
    )

    # 権限のバリデーション
    @field_validator("authority", mode="before")
    def validate_authority(cls: Type["User"], value: str | Role) -> Role:
        """
        権限 (authority) フィールドの値を検証します。

        Args:
            cls (Type["User"]): クラス自身。
            value (str | Role): バリデーション対象の値。

        Returns:
            Role: 検証を通過した列挙型の値。

        Raises:
            ValueError: 権限が無効な場合に発生。
        """
        try:
            # 入力値が列挙型でなければ変換を試みる
            return Role(value)
        except ValueError:
            raise ValueError(f"Invalid role specified: {value}. Valid roles are: {list(Role)}")

    # APIドキュメントに表示される例
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


# セッション情報を定義するモデル
class Session(SQLModel, table=True):
    """
    セッションモデル: 各ユーザが作成するセッションを表現。
    """

    id: int | None = Field(
        None,
        primary_key=True,
        title="セッションID",
        description="セッションを一意に識別するためのID",
    )
    session_name: str = Field(
        "NewSession",
        sa_column=Column(Unicode(255)),  # 最大255文字のセッション名
        title="名前",
        description="セッション名",
    )
    pub_data: datetime | None = Field(
        None,
        title="公開日時",
        description="セッションの公開日時",
    )
    user_id: str = Field(
        ...,
        max_length=255,
        foreign_key="user.id",  # ユーザモデルへの外部キー
        title="ユーザID",
        description="関連するユーザのID",
    )

    # セッションとチャットログのリレーション (1対多)
    chat_logs: list["ChatLog"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    # セッションとユーザのリレーション (多対1)
    user: User | None = Relationship(back_populates="sessions")

    # APIドキュメントに表示される例
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "session_name": "新しいセッション",
                "pub_data": "2024-06-29T12:35:00",
                "user_id": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
            }
        }


# チャットログ情報を定義するモデル
class ChatLog(SQLModel, table=True):
    """
    チャットログモデル: セッション内でのチャット内容を保存。
    """

    id: int | None = Field(
        None,
        primary_key=True,
        title="チャットID",
        description="チャットを一意に識別するためのID",
    )
    message: str = Field(
        ...,
        sa_column=Column(Unicode(255), index=True),  # インデックスを追加
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
        index=True,
    )
    session_id: int | None = Field(
        None,
        foreign_key="session.id",  # セッションモデルへの外部キー
        title="セッションID",
        description="関連するセッションのID",
    )

    # チャットログとセッションのリレーション (多対1)
    session: Optional["Session"] = Relationship(back_populates="chat_logs")

    # APIドキュメントに表示される例
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
