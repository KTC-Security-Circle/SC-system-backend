from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from api.app.models import Users, ErrorLog, Sessions
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user
from api.app.dto import ErrorLogDTO
from api.app.role import Role, role_required
from typing import Optional
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/errorlog/", response_model=ErrorLogDTO, tags=["errorlog_post"])
@role_required(Role.ADMIN)
async def create_error_log(
    errorlog: ErrorLog,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    error_log_data = ErrorLog(
        error_message=errorlog.error_message,
        pub_data=datetime.now(),
        session_id=errorlog.session_id,
    )
    await add_db_record(engine, error_log_data)
    logger.error("エラーが発生しました。")
    logger.error(f"エラーID:{error_log_data.id}")
    logger.error(f"エラー名:{error_log_data.error_message}")
    logger.error(f"投稿日時:{error_log_data.pub_data}")
    logger.error(f"セッションID:{error_log_data.session_id}")
    error_dto = ErrorLogDTO(
        id=error_log_data.id,
        error_message=error_log_data.error_message,
        pub_data=error_log_data.pub_data,
        session_id=error_log_data.session_id
    )
    return error_dto


@router.get("/app/view/errorlog/", response_model=list[ErrorLogDTO], tags=["errorlog_get"])
@role_required(Role.ADMIN)  # admin権限が必要
async def view_errorlog(
    session_id: Optional[int] = None,
    error_message_like: Optional[str] = None,  # メッセージの部分一致フィルタ
    order_by: Optional[str] = None,  # ソート基準のフィールド名
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {}
    like_conditions = {}

    if session_id:
        conditions["session_id"] = session_id

    if error_message_like:
        like_conditions["error_message"] = error_message_like

    errorlog = await select_table(
        engine,
        ErrorLog,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by
    )

    logger.debug(errorlog)

    errorlog_dto_list = [
        ErrorLogDTO(
            id=log.id,
            error_message=log.error_message,
            pub_data=log.pub_data,
            session_id=log.session_id
        )
        for log in errorlog
    ]

    return errorlog_dto_list



@router.put("/app/update/errorlog/{errorlog_id}/", response_model=ErrorLogDTO, tags=["errorlog_put"])
@role_required(Role.ADMIN)  # admin権限が必要
async def update_errorlog(
    errorlog_id: int,
    updates: dict[str, str],
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {"id": errorlog_id}
    updated_record = await update_record(engine, ErrorLog, conditions, updates)
    updated_errorlog_dto = ErrorLogDTO(
        id=updated_record.id,
        error_message=updated_record.error_message,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id
    )
    return updated_errorlog_dto


@router.delete("/app/delete/errorlog/{errorlog_id}/", response_model=dict, tags=["errorlog_delete"])
@role_required(Role.ADMIN)  # admin権限が必要
async def delete_errorlog(
    errorlog_id: int,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    # エラーログを取得
    conditions = {"id": errorlog_id}
    # errorlog_to_delete = await select_table(engine, ErrorLog, conditions)

    # if not errorlog_to_delete:
    #     raise HTTPException(status_code=404, detail="エラーログが見つかりません")

    # # エラーログのセッションIDからセッションを取得し、ユーザーIDを確認
    # session_conditions = {"id": errorlog_to_delete[0].session_id}
    # session = await select_table(engine, Sessions, session_conditions)

    # if not session or session[0].user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="このエラーログを削除する権限がありません")

    # 削除を実行
    result = await delete_record(engine, ErrorLog, conditions)
    return result
