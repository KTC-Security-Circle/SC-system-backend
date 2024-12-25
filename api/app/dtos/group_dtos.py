from enum import Enum

from pydantic import Field
from sqlmodel import SQLModel


class GroupDTO(SQLModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Development Team",
                "description": "開発チーム",
            }
        }


class GroupCreateDTO(SQLModel):
    name: str = Field(..., max_length=100, title="グループ名", description="グループの名前")
    description: str | None = Field(None, max_length=255, title="説明", description="グループの説明")

    class Config:
        schema_extra = {
            "example": {
                "name": "Development Team",
                "description": "開発チーム",
            }
        }


class GroupUpdateDTO(SQLModel):
    name: str | None = Field(None, max_length=100, title="グループ名", description="グループの名前")
    description: str | None = Field(None, max_length=255, title="説明", description="グループの説明")

    class Config:
        schema_extra = {
            "example": {
                "name": "New Team Name",
                "description": "新しい説明内容",
            }
        }


class GroupOrderBy(str, Enum):
    id = "id"
    name = "name"
    description = "description"


class GroupSearchDTO(SQLModel):
    name: str | None = Field(None, title="グループ名", description="グループ名で検索")
    name_like: str | None = Field(None, title="部分一致検索", description="部分一致でグループ名を検索")
    description_like: str | None = Field(None, title="説明の部分一致検索", description="部分一致で説明を検索")

    class Config:
        schema_extra = {
            "example": {
                "name": "Development Team",
                "name_like": "Dev",
                "description_like": "開発",
            }
        }
