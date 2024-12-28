import logging

import azure.functions as func

from api.app_fastapi import app
from api.logger import getLogger

# ロガーを設定し、ログレベルをDEBUGに設定
logger = getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)

# FastAPIアプリをAzure FunctionsのASGIアプリケーションとして設定
function_app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
