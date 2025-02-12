from pydantic import Field
from sqlmodel import SQLModel


class WorldDTO(SQLModel):
    id: int
    name: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "技術・科学"
            }
        }


class WorldCreateDTO(SQLModel):
    name: str | None = Field(
        default="未設定", 
        max_length=150
    )

class WorldOrderBy(str):
    name = "name"
    pub_data = "pub_data"


class WorldSearchDTO(SQLModel):
    name: str | None = None
    name_like: str | None = None


class WorldUpdateDTO(SQLModel):
    name: str | None = Field(None, max_length=150)

