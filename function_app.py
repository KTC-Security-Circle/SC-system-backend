import logging
import azure.functions as func
from api.app_fastapi import app  # `app.py` から FastAPI アプリをインポート
from os.path import join, dirname
from dotenv import load_dotenv

# ロガーの設定
logger = logging.getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

dotenv_path = join(dirname(__file__), "secret/.env")
load_dotenv(dotenv_path)

# Azure Functions用のASGIアプリとして登録
asgi_app = func.AsgiFunctionApp(
    app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
