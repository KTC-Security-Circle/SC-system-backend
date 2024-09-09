from api.app.models import ChatLog
from api.app.dtos.chatlog_dtos import (
    ChatLogDTO,
    ChatCreateDTO,
    ChatOrderBy,
    ChatSearchDTO,
    ChatUpdateDTO
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

@router.post("/app/input/chat/", response_model=ChatLogDTO, tags=["chat_post"])
@role_required(Role.ADMIN)
async def create_chatlog(
    chatlog: ChatCreateDTO,  # DTOを使用
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    chat_log_data = ChatLog(
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=chatlog.pub_data or datetime.now(),  # 日時が指定されていない場合は現在時刻を使用
        session_id=chatlog.session_id,
    )
    await add_db_record(engine, chat_log_data)
    logger.info("新しいチャットを登録します。")

    logger.info(f"チャットID:{chat_log_data.id}")
    logger.info(f"チャット内容:{chat_log_data.message}")
    logger.info(f"ボットの返信:{chat_log_data.bot_reply}")
    logger.info(f"投稿日時:{chat_log_data.pub_data}")
    logger.info(f"セッションID:{chat_log_data.session_id}")

    chat_dto = ChatLogDTO(
        id=chat_log_data.id,
        message=chat_log_data.message,
        bot_reply=chat_log_data.bot_reply,
        pub_data=chat_log_data.pub_data,
        session_id=chat_log_data.session_id
    )
    return chat_dto


@router.get("/app/view/chat/", response_model=list[ChatLogDTO], tags=["chat_get"])
@role_required(Role.ADMIN)
async def view_chatlog(
    search_params: ChatSearchDTO = Depends(),  # メッセージの部分一致フィルタ
    order_by: Optional[ChatOrderBy] = None,  # ソート基準のフィールド名
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    conditions_dict = {}
    like_conditions = {}

    if search_params.session_id is not None:
        conditions_dict["session_id"] = search_params.session_id

    if search_params.message_like:
        like_conditions["message"] = search_params.message_like

    chatlog = await select_table(
        engine,
        ChatLog,
        conditions_dict,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by
    )

    chatlog_dto_list = [
        ChatLogDTO(
            id=log.id,
            message=log.message,
            bot_reply=log.bot_reply,
            pub_data=log.pub_data,
            session_id=log.session_id
        )
        for log in chatlog
    ]

    return chatlog_dto_list


@router.put("/app/update/chat/{chat_id}/", response_model=ChatLogDTO, tags=["chat_put"])
@role_required(Role.ADMIN)  # admin権限が必要
async def update_chatlog(
    chat_id: int,
    updates: ChatUpdateDTO,  # DTOを使用
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)  # 送信されていないフィールドは無視
    updated_record = await update_record(engine, ChatLog, conditions, updates_dict)

    updated_chatlog_dto = ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id
    )
    return updated_chatlog_dto


@router.delete("/app/delete/chat/{chat_id}/", response_model=dict, tags=["chat_delete"])
@role_required(Role.ADMIN)  # admin権限が必要
async def delete_chatlog(
    chat_id: int,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    # 削除対象のチャットログを取得
    conditions = {"id": chat_id}
    # chatlog_to_delete = await select_table(engine, ChatLog, conditions)

    # if not chatlog_to_delete:
    #     raise HTTPException(status_code=404, detail="チャットログが見つかりません")

    # # チャットログのセッションIDからセッションを取得し、ユーザーIDを確認
    # session_conditions = {"id": chatlog_to_delete[0].session_id}
    # session = await select_table(engine, Session, session_conditions)

    # if not session or session[0].user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="このチャットログを削除する権限がありません")

    # 削除を実行
    result = await delete_record(engine, ChatLog, conditions)
    return result
