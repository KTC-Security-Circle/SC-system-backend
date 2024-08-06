from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from api.app.database.database import get_engine
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = next(get_engine())
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

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

app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:7071",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
