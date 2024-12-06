# 標準ライブラリ
import logging

# サードパーティライブラリ
import azure.functions as func

# ローカルモジュール
# from api.app_fastapi import app as app_app  # 必要な場合に有効化
from api.demo_fastapi import app as demo_app
from api.logger import getLogger

# ロガーの設定
# "azure_functions.fastapi" という名前でカスタムロガーを作成し、ログレベルを DEBUG に設定
logger = getLogger("azure_functions.fastapi", logging.DEBUG)

# FastAPI アプリを Azure Functions の ASGI アプリケーションとして登録
# 認証レベルを ANONYMOUS（無認証）に設定
function_app = func.AsgiFunctionApp(
    app=demo_app,  # 使用する FastAPI アプリケーション
    http_auth_level=func.AuthLevel.ANONYMOUS,  # HTTP トリガーの認証レベルを指定
)

# デバッグ情報出力用のログ（オプション）
logger.debug("Azure Functions ASGI application initialized with demo FastAPI app.")
