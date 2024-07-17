from fastapi import APIRouter
from datetime import datetime
from api.app.models import Sessions
from api.app.database.database import engine,add_db_record,select_table,update_record,delete_record
from typing import Optional
import json

router = APIRouter()

@router.post("/app/input/session/", response_model=Sessions)
async def create_sessions(session: Sessions):
  session_data = Sessions(
    id=session.id,
    session_name=session.session_name,
    pub_data=datetime.now(),
    user_id=session.user_id,
  )
  await add_db_record(engine,session_data)
  print(f"新しいセッションを登録します。\n\
セッションID:{session.id}\nセッション名:{session.session_name}\n投稿日時:{session.pub_data}\nユーザーID:{session.user_id}")
  return session_data

@router.get("/app/view/session/", response_model=list[Sessions])
async def view_sessions(conditions: Optional[str]  = None,limit: Optional[int] =None, offset: Optional[int] = 0):
  if conditions != None:
    conditions = json.loads(conditions)
  sessions = await select_table(engine,Sessions,conditions=conditions, limit=limit, offset=offset)
  print(sessions)
  return sessions

@router.put("/app/update/session/{session_id}/", response_model=Sessions)
async def update_sessions(session_id: int, updates: dict[str, str]):
  conditions = {"id": session_id}
  updated_record = await update_record(engine, Sessions, conditions, updates)
  return updated_record

@router.delete("/app/delete/session/{session_id}/", response_model=dict)
async def delete_session(session_id: int):
  conditions = {"id": session_id}
  result = await delete_record(engine, Sessions, conditions)
  return result

@router.delete("/app/all_delete/session/{session_id}/", response_model=dict)
async def delete_session(session_id: int):
  conditions = {"id": session_id}
  result = await delete_record(engine, Sessions, conditions)
  return result
