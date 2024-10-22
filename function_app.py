import logging
import azure.functions as func
from api.app_fastapi import app

# 正式なAPI用のインポート
from api.app.routers import auth as app_auth, messages as app_messages
from api.app.routers import users as app_users, chats as app_chats, \
    sessions as app_sessions, error_log as app_error_log


# デモ用APIのインポート
from api.demo.routers import users as demo_users, chats as demo_chats, \
    sessions as demo_sessions, error_log as demo_error_log

# http://localhost:7071/ or http://localhost:7071/docs

# 正式なAPIのルータを登録


@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello world"}

app.include_router(app_auth.router, prefix="/api", tags=["api"])
app.include_router(app_messages.router, prefix="/api", tags=["api"])
app.include_router(app_users.router, prefix="/api", tags=["api"])
app.include_router(app_chats.router, prefix="/api", tags=["api"])
app.include_router(app_sessions.router, prefix="/api", tags=["api"])
app.include_router(app_error_log.router, prefix="/api", tags=["api"])


# デモ用APIのルータを登録
app.include_router(demo_users.router, prefix="/demo", tags=["demo"])
app.include_router(demo_chats.router, prefix="/demo", tags=["demo"])
app.include_router(demo_sessions.router, prefix="/demo", tags=["demo"])
app.include_router(demo_error_log.router, prefix="/demo", tags=["demo"])

# ロガーの設定
logger = logging.getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

asgi_app = func.AsgiFunctionApp(
    app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
