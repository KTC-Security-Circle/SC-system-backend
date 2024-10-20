# FastAPI関連の共通インポート
from fastapi import APIRouter, Depends, HTTPException, Response

# 日付関連
from datetime import datetime

# セキュリティ関連
from api.app.security.jwt_token import get_current_user

# 権限関連
from api.app.role import Role, role_required

# 型指定
from typing import Optional

# ログ関連
from api.logger import getLogger

# データベース関連
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)

# ユーザーモデル
from api.app.models import User

# sc-system-ai
from sc_system_ai import main as SC_AI

# 共通のインスタンス
logger = getLogger(__name__)
router = APIRouter()