import logging
import azure.functions as func
from api.app_fastapi import app  # `app.py` から FastAPI アプリをインポート

# ロガーの設定
logger = logging.getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

# Azure Functions用のASGIアプリとして登録
asgi_app = func.AsgiFunctionApp(
    app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
