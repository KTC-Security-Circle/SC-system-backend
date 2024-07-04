from fastapi import FastAPI
from sqlmodel import SQLModel
from api.app.database.database import get_engine
from contextlib import asynccontextmanager

engine = get_engine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

# FastAPIアプリケーションのインスタンスを作成
tags_metadata = [
    {
        "name": "root",
        "description": "ルートエンドポイント",
    },
    {
        "name": "api",
        "description": "運用用APIのエンドポイント",
    },
    {
        "name": "demo",
        "description": "デモ用APIのエンドポイント",
    },
]

app = FastAPI(openapi_tags=tags_metadata,lifespan=lifespan)