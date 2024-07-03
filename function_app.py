import logging
from fastapi import FastAPI
import azure.functions as func

# 正式なAPI用のインポート
from api.app.routers import auth as app_auth, messages as app_messages

# デモ用APIのインポート
from api.demo.routers import auth as demo_auth,\
messages as demo_messages, users as demo_users, chats as demo_chats,\
sessions as demo_sessions, error_log as demo_error_log
from api.demo.routers import auth as demo_auth, messages as demo_messages

# http://localhost:7071/ or http://localhost:7071/docs

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
app = FastAPI(openapi_tags=tags_metadata)

# 正式なAPIのルータを登録
@app.get("/", tags=["root"])
async def root():
    return {"message":"Hello world"}

app.include_router(app_auth.router, prefix="/api", tags=["api"])
app.include_router(app_messages.router, prefix="/api" , tags=["api"])

# デモ用APIのルータを登録
app.include_router(demo_auth.router, prefix="/demo", tags=["demo"])
app.include_router(demo_messages.router, prefix="/demo", tags=["demo"])
<<<<<<< HEAD
app.include_router(demo_users.router, prefix="/demo", tags=["demo"])
app.include_router(demo_chats.router, prefix="/demo", tags=["demo"])
app.include_router(demo_sessions.router, prefix="/demo", tags=["demo"])
app.include_router(demo_error_log.router, prefix="/demo", tags=["demo"])
=======
>>>>>>> origin

# ロガーの設定
logger = logging.getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)