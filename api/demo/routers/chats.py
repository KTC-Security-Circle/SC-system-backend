from fastapi import APIRouter,HTTPException
from ..models.database import ChatLog
from ..schemas.message import Message
from datetime import datetime
from ...api_db_conn import database
import sqlite3

router = APIRouter()

@database
async def insert_chat_log(cur, chatlog: ChatLog):
    try:
        cur.execute("""
            INSERT INTO chatlog (id, message, bot_reply, pub_data, session_id)
            VALUES (?, ?, ?, ?, ?)
        """, (chatlog.id, chatlog.message, chatlog.bot_reply, chatlog.pub_data, chatlog.session_id))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="チャットIDが既に存在します")

@router.post("/chat/", response_model=Message)
async def create_chatlog(chatlog: ChatLog):
  chatlog.pub_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  await insert_chat_log(chatlog)
  print(f"新しいチャットを登録します。\n\
チャットID:{chatlog.id}\nチャット内容:{chatlog.message}\nボットの返信:{chatlog.bot_reply}\n\
投稿日時:{chatlog.pub_data}\nセッションID:{chatlog.session_id}")
  result = Message(content=f"SCシステム: {chatlog.bot_reply}")
  return result