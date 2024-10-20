from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from api.app.database.database import get_engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = next(get_engine())
    SQLModel.metadata.create_all(engine)
    yield
    # SQLModel.metadata.drop_all(engine)

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
    {
        "name": "chat_post",
        "description": "新しいchatをデータベースに送信するAPI"
    },
    {
        "name": "chat_get",
        "description": "データベースから指定した条件のchatを受け取るAPI"
    },
    {
        "name": "chat_put",
        "description": "既存のchatを編集してデータベースを更新するAPI"
    },
    {
        "name": "chat_delete",
        "description": "指定した条件のchatを削除するAPI"
    },
    {
        "name": "errorlog_post",
        "description": "新しいerrorlogをデータベースに送信するAPI"
    },
    {
        "name": "errorlog_get",
        "description": "データベースから指定した条件のerrorlogを受け取るAPI"
    },
    {
        "name": "errorlog_put",
        "description": "既存のerrorlogを編集してデータベースを更新するAPI"
    },
    {
        "name": "errorlog_delete",
        "description": "指定した条件のerrorlogを削除するAPI"
    },
    {
        "name": "sessions_post",
        "description": "新しいsessionをデータベースに送信するAPI"
    },
    {
        "name": "sessions_get",
        "description": "データベースから指定した条件のsessionを受け取るAPI"
    },
    {
        "name": "sessions_put",
        "description": "既存のsessionを編集してデータベースを更新するAPI"
    },
    {
        "name": "sessions_delete",
        "description": "指定した条件のsessionを削除するAPI"
    },
    {
        "name": "users_post",
        "description": "新しいuserをデータベースに送信するAPI"
    },
    {
        "name": "users_get",
        "description": "データベースから指定した条件のuserを受け取るAPI"
    },
    {
        "name": "users_put",
        "description": "既存のuserを編集してデータベースを更新するAPI"
    },
    {
        "name": "users_delete",
        "description": "指定した条件のuserを削除するAPI"
    },
    {
        "name": "signup",
        "description": "新規ユーザーを登録するAPI"
    },
    {
        "name": "login",
        "description": "userのemailとpasswordに基づいてJWTTokenを返すAPI"
    },
    {
        "name": "users",
        "description": "userの情報を送信すると、その情報をそのまま返すデモAPI"
    },
    {
        "name": "sessions",
        "description": "sessionsの情報を送信すると、その情報をそのまま返すデモAPI"
    },
    {
        "name": "chat",
        "description": "chatの情報を送信すると、その情報をそのまま返すデモAPI"
    },
    {
        "name": "errorlog",
        "description": "errorlogの情報を送信すると、その情報をそのまま返すデモAPI"
    }
]

app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:7071",
    "https://sc-test-api.azurewebsites.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)