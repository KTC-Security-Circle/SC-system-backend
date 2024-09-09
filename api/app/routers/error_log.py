from api.app.models import  ErrorLog
from api.app.security.jwt_token import get_current_user
from api.app.dtos.errorlog_dtos import (
    ErrorLogDTO,
    ErrorLogCreateDTO,
    ErrorLogOrderBy,
    ErrorLogSearchDTO,
    ErrorLogUpdateDTO
)
from api.app.routers import (
    logger,
    router,
    Depends,
    datetime,
    get_current_user,
    Role,
    role_required,
    Optional,
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
    User,
)


@router.post("/app/input/errorlog/", response_model=ErrorLogDTO, tags=["errorlog_post"])
@role_required(Role.ADMIN)
async def create_error_log(
    errorlog: ErrorLogCreateDTO,  # DTOを使用
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    error_log_data = ErrorLog(
        error_message=errorlog.error_message,
        pub_data=errorlog.pub_data or datetime.now(),  # 日時が指定されていない場合は現在時刻を使用
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
    search_params: ErrorLogSearchDTO = Depends(),
    order_by: Optional[ErrorLogOrderBy] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    conditions = {}
    like_conditions = {}

    if search_params.session_id:
        conditions["session_id"] = search_params.session_id

    if search_params.error_message_like:
        like_conditions["error_message"] = search_params.error_message_like

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
@role_required(Role.ADMIN)
async def update_errorlog(
    errorlog_id: int,
    updates: ErrorLogUpdateDTO,  # DTOを使用
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    conditions = {"id": errorlog_id}
    updates_dict = updates.model_dump(exclude_unset=True)  # 送信されていないフィールドは無視
    updated_record = await update_record(engine, ErrorLog, conditions, updates_dict)

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
    current_user: User = Depends(get_current_user)
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
