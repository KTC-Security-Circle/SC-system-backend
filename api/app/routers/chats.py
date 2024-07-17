from fastapi import APIRouter
from datetime import datetime
from api.app.models import ChatLog
from api.app.database.database import engine,add_db_record,select_table,update_record,delete_record
from typing import Optional
import json

router = APIRouter()

@router.post("/app/input/chat/", response_model=ChatLog)
async def create_chatlog(chatlog: ChatLog):
  chat_log_data = ChatLog(
    id=chatlog.id,
    message=chatlog.message,
    bot_reply=chatlog.bot_reply,
    pub_data=datetime.now(),
    session_id=chatlog.session_id
  )
  await add_db_record(engine,chat_log_data)  
  print(f"新しいチャットを登録します。\n\
チャットID:{chatlog.id}\nチャット内容:{chatlog.message}\nボットの返信:{chatlog.bot_reply}\n\
投稿日時:{chatlog.pub_data}\nセッションID:{chatlog.session_id}")
  return chat_log_data

@router.get("/app/view/chat/", response_model=list[ChatLog])
async def view_chatlog(conditions: Optional[str]  = None,limit: Optional[int] =None, offset: Optional[int] = 0):
  if conditions != None:
    conditions = json.loads(conditions)
  chatlog_all = await select_table(engine, ChatLog, conditions=conditions, limit=limit, offset=offset)
  print(chatlog_all)
  return chatlog_all

@router.put("/app/update/chat/{chat_id}/", response_model=ChatLog)
async def update_chatlog(chat_id: int, updates: dict[str, str]):
  conditions = {"id": chat_id}
  updated_record = await update_record(engine, ChatLog, conditions, updates)
  return updated_record

@router.delete("/app/delete/chat/{chat_id}/", response_model=dict)
async def delete_chatlog(chat_id: int):
  conditions = {"id": chat_id}
  result = await delete_record(engine, ChatLog, conditions)
  return result