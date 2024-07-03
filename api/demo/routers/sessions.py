from fastapi import APIRouter,HTTPException
from ..models.database import Sessions
from ..schemas.message import Message
from datetime import datetime
from ...api_db_conn import database
import sqlite3

router = APIRouter()

@database
async def insert_session(cur, session: Sessions):
    try:
        cur.execute("""
            INSERT INTO sessions (id, session_name, pub_data, user_id)
            VALUES (?, ?, ?, ?)
        """, (session.id, session.session_name, session.pub_data, session.user_id))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="ユーザーIDが既に存在します")

@router.post("/sessions/", response_model=Message)
async def create_Session(session: Sessions):
  session.pub_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  await insert_session(session)
  print(f"新しいセッションを登録します。\n\
セッションID:{session.id}\nセッション名:{session.session_name}\n投稿日時:{session.pub_data}\nユーザーID:{session.user_id}")
  result = Message(content=f"新しいセッション: {session.session_name}")
  return result