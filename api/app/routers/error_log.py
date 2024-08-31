from fastapi import APIRouter, Depends
from datetime import datetime
from api.app.models import Users, ErrorLog  # SQLModelモデルをインポート
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user
from typing import Optional
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/errorlog/", response_model=ErrorLog, tags=["errorlog_post"])
async def create_error_log(
    errorlog: ErrorLog,
    engine=Depends(get_engine)
):
    error_log_data = ErrorLog(
        id=errorlog.id,
        error_message=errorlog.error_message,
        pub_data=datetime.now(),
        session_id=errorlog.session_id,
    )
    await add_db_record(engine, error_log_data)
    logger.error("エラーが発生しました。")
    logger.error(f"エラーID:{errorlog.id}")
    logger.error(f"エラー名:{errorlog.error_message}")
    logger.error(f"投稿日時:{errorlog.pub_data}")
    logger.error(f"セッションID:{errorlog.session_id}")
    return error_log_data


@router.get("/app/view/errorlog/", response_model=list[ErrorLog], tags=["errorlog_get"])
async def view_errorlog(
    conditions: Optional[dict] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine)
):
    errorlog = await select_table(engine, ErrorLog, conditions,offset, limit)
    logger.debug(errorlog)
    return errorlog


@router.put("/app/update/errorlog/{errorlog_id}/", response_model=ErrorLog, tags=["errorlog_put"])
async def update_errorlog(
    errorlog_id: int,
    updates: dict[str, str],
    engine=Depends(get_engine)
):
    conditions = {"id": errorlog_id}
    updated_record = await update_record(engine, ErrorLog, conditions, updates)
    return updated_record


@router.delete("/app/delete/errorlog/{errorlog_id}/", response_model=dict, tags=["errorlog_delete"])
async def delete_errorlog(
    errorlog_id: int,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {"id": errorlog_id}
    result = await delete_record(engine, ErrorLog, conditions)
    return result
