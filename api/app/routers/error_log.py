from fastapi import APIRouter
from datetime import datetime
from api.app.models import ErrorLog  # SQLModelモデルをインポート
from api.app.database.database import engine,add_db_record,select_table,update_record,delete_record
from typing import Optional

router = APIRouter()

@router.post("/app/input/errorlog/", response_model=ErrorLog)
async def create_error_log(errorlog: ErrorLog):
  error_log_data = ErrorLog(
    id=errorlog.id,
    error_message=errorlog.error_message,
    pub_data=datetime.now(),
    session_id=errorlog.session_id
  )
  await add_db_record(engine,error_log_data)
  print(f"エラーが発生しました。\n\
エラーID:{errorlog.id}\nエラー名:{errorlog.error_message}\n投稿日時:{errorlog.pub_data}\nセッションID:{errorlog.session_id}")
  return error_log_data

@router.get("/app/view/errorlog/", response_model=list[ErrorLog])
async def view_errorlog(limit: Optional[int] =None, offset: Optional[int] = 0):
  errorlog = await select_table(engine,ErrorLog,offset,limit)
  print(errorlog)
  return errorlog

@router.put("/app/update/errorlog/{errorlog_id}/", response_model=ErrorLog)
async def update_errorlog(errorlog_id: int, updates: dict[str, str]):
  conditions = {"id": errorlog_id}
  updated_record = await update_record(engine, ErrorLog, conditions, updates)
  return updated_record

@router.delete("/app/delete/errorlog/{errorlog_id}/", response_model=dict)
async def delete_errorlog(errorlog_id: int):
    conditions = {"id": errorlog_id}
    result = await delete_record(engine, ErrorLog, conditions)
    return result