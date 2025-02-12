from pydantic import Field
from sqlmodel import SQLModel


class MajorDTO(SQLModel):
    id: int
    name: str
    world_id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "コンピュータサイエンス",
                "world_id": 1,
            }
        }


class MajorCreateDTO(SQLModel):
    name: str | None = Field(
        default="未設定", 
        max_length=150
    )
    world_id: int

class MajorOrderBy(str):
    name = "name"
    pub_data = "pub_data"


class MajorSearchDTO(SQLModel):
    name: str | None = None
    name_like: str | None = None
    world_id: int | None = None


class MajorUpdateDTO(SQLModel):
    name: str | None = Field(None, max_length=150)
