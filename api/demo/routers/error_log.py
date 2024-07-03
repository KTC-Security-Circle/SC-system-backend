from fastapi import APIRouter,HTTPException
from ..models.database import ErrorLog
from ..schemas.message import Message
from datetime import datetime
from ...api_db_conn import database
import sqlite3

router = APIRouter()

@database
async def insert_error_log(cur, errorlog: ErrorLog):
    try:
        cur.execute("""
            INSERT INTO errorlog (id, error_message, pub_data, session_id)
            VALUES (?, ?, ?, ?)
        """, (errorlog.id, errorlog.error_message, errorlog.pub_data, errorlog.session_id))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="ユーザーIDが既に存在します")

@router.post("/errorlog/", response_model=Message)
async def create_errorlog(errorlog: ErrorLog):
  errorlog.pub_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  await insert_error_log(errorlog)
  print(f"エラーが発生しました。\n\
エラーID:{errorlog.id}\nエラー名:{errorlog.error_message}\n投稿日時:{errorlog.pub_data}\nセッションID:{errorlog.session_id}")
  result = Message(content=f"エラー: {errorlog.error_message}")
  return result