from datetime import datetime

from pydantic import Field
from sqlmodel import SQLModel


class SchoolInfoDTO(SQLModel):
    id: int
    title: str
    contents: str
    pub_date: datetime | None = None
    updated_at: datetime | None = None
    created_by: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "本校設立年",
                "contents": "本校は2024年に設立されました。",
                "pub_date": "2024-06-29T12:34:56",
                "updated_at": "2024-07-01T09:30:00",
                "created_by": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
            }
        }


class SchoolInfoCreateDTO(SQLModel):
    title: str = Field(..., max_length=255, title="タイトル", description="学校情報のタイトル")
    contents: str = Field(..., max_length=1000, title="内容", description="学校情報の内容")
    pub_date: datetime | None = Field(None, title="公開日時", description="学校情報の公開日時")
    updated_at: datetime | None = Field(None, title="更新日時", description="学校情報の最終更新日時")

    class Config:
        schema_extra = {
            "example": {
                "title": "本校設立年",
                "contents": "本校は2024年に設立されました。",
                "pub_date": "2024-06-29T12:34:56",
                "updated_at": "2024-07-01T09:30:00",
            }
        }


class SchoolInfoUpdateDTO(SQLModel):
    title: str | None = Field(..., max_length=255, title="タイトル", description="学校情報のタイトル")
    contents: str | None = Field(None, max_length=1000, title="内容", description="学校情報の内容")
    pub_date: datetime | None = Field(None, title="公開日時", description="学校情報の公開日時")
    updated_at: datetime | None = Field(None, title="更新日時", description="学校情報の最終更新日時")

    class Config:
        schema_extra = {
            "example": {
                "title": "本校設立年",
                "contents": "本校の創立者は山田太郎氏です。",
                "pub_date": "2024-06-30T08:00:00",
                "updated_at": "2024-07-02T10:00:00",
            }
        }


class SchoolInfoSearchDTO(SQLModel):
    title_like: str | None = Field(None, title="内容の部分一致", description="内容で部分一致検索")
    contents_like: str | None = Field(None, title="内容の部分一致", description="内容で部分一致検索")
    created_by: str | None = Field(None, title="作成者ID", description="作成者IDで検索")

    class Config:
        schema_extra = {
            "example": {
                "title_like": "設立年",
                "contents_like": "設立",
                "created_by": "xxxxxxxx-xxxx-Mxxx-xxxx-xxxxxxxxxxxx",
            }
        }

class SchoolInfoTitleDTO(SQLModel):
    id: int
    title: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "本校設立年",
            }
        }
