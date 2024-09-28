import logging
import os
import azure.functions as func
from app_fastapi import app as fastapi_app

# 正式なAPI用のインポート
from api.app.routers import auth as app_auth, messages as app_messages
from api.app.routers import (
    users as app_users,
    chats as app_chats,
    sessions as app_sessions,
    error_log as app_error_log,
)


# デモ用APIのインポート
from api.demo.routers import (
    users as demo_users,
    chats as demo_chats,
    sessions as demo_sessions,
    error_log as demo_error_log,
)

# Application Insights関連
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

configure_azure_monitor(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)
FastAPIInstrumentor.instrument_app(fastapi_app)

# http://localhost:7071/ or http://localhost:7071/docs

# 正式なAPIのルータを登録


@fastapi_app.get("/", tags=["root"])
async def root():
    return {"message": "Hello world"}


fastapi_app.include_router(app_auth.router, prefix="/api", tags=["api"])
fastapi_app.include_router(app_messages.router, prefix="/api", tags=["api"])
fastapi_app.include_router(app_users.router, prefix="/api", tags=["api"])
fastapi_app.include_router(app_chats.router, prefix="/api", tags=["api"])
fastapi_app.include_router(app_sessions.router, prefix="/api", tags=["api"])
fastapi_app.include_router(app_error_log.router, prefix="/api", tags=["api"])


# デモ用APIのルータを登録
fastapi_app.include_router(demo_users.router, prefix="/demo", tags=["demo"])
fastapi_app.include_router(demo_chats.router, prefix="/demo", tags=["demo"])
fastapi_app.include_router(demo_sessions.router, prefix="/demo", tags=["demo"])
fastapi_app.include_router(demo_error_log.router, prefix="/demo", tags=["demo"])

# ロガーの設定
logger = logging.getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
