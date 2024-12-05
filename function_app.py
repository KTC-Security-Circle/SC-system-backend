import logging

import azure.functions as func

from api.demo_fastapi import app as demo_app

# from api.app_fastapi import app as app_app
from api.logger import getLogger

# ロガーを設定し、ログレベルをDEBUGに設定
logger = getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

# FastAPIアプリをAzure FunctionsのASGIアプリケーションとして設定
function_app = func.AsgiFunctionApp(
    app=demo_app, http_auth_level=func.AuthLevel.ANONYMOUS
)
