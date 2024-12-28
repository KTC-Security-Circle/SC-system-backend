import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine

from api.demo.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.demo.database.engine import get_engine
from api.demo.dtos.chatlog_dtos import (
    ChatCreateDTO,
    ChatLogDTO,
    ChatOrderBy,
    ChatSearchDTO,
    ChatUpdateDTO,
)
from api.demo.models import ChatLogDemo
from api.logger import getLogger

router = APIRouter()
logger = getLogger("chatlog_router")
logger.setLevel(logging.DEBUG)


@router.post("/input/chat", response_model=ChatLogDTO, tags=["chat_post"])
async def create_chatlog(
    chatlog: ChatCreateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
) -> ChatLogDTO:
    logger.info("チャット作成リクエストを受け付けました。ユーザーID:")

    try:
        chat_log_data = ChatLogDemo(
            message=chatlog.message,
            bot_reply="これはテストリプライです。",
            pub_data=chatlog.pub_data or datetime.now(),
            session_id=1,
        )
        await add_db_record(engine, chat_log_data)

        # 最後にDTOをJSON形式で返す
        dto = ChatLogDTO(
            id=chat_log_data.id,
            message=chat_log_data.message,
            bot_reply=chat_log_data.bot_reply,
            pub_data=chat_log_data.pub_data,
            session_id=1,
        )

        return dto

    except Exception as e:
        logger.error(f"チャットログ作成中にエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"チャットログの作成中にエラーが発生しました。{str(e)}",
        ) from e


@router.get("/view/chat", response_model=list[ChatLogDTO], tags=["chat_get"])
async def view_chatlog(
    search_params: Annotated[ChatSearchDTO, Depends()],
    engine: Annotated[Engine, Depends(get_engine)],
    order_by: ChatOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
) -> list[ChatLogDTO]:
    logger.info(f"チャットログ取得リクエストを受け付けました。検索条件: {search_params}")

    conditions_dict = {}
    like_conditions = {}

    if search_params.session_id is not None:
        conditions_dict["session_id"] = search_params.session_id

    if search_params.message_like:
        like_conditions["message"] = search_params.message_like

    chatlog = await select_table(
        engine,
        ChatLogDemo,
        conditions_dict,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"チャットログ取得完了: {len(chatlog)}件")

    chatlog_dto_list = [
        ChatLogDTO(
            id=log.id,
            message=log.message,
            bot_reply=log.bot_reply,
            pub_data=log.pub_data,
            session_id=log.session_id,
        )
        for log in chatlog
    ]

    return chatlog_dto_list


@router.put("/update/chat/{chat_id}", response_model=ChatLogDTO, tags=["chat_put"])
async def update_chatlog(
    chat_id: int,
    updates: ChatUpdateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
) -> ChatLogDTO:
    logger.info(f"チャットログ更新リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)
    updated_record = await update_record(engine, ChatLogDemo, conditions, updates_dict)

    logger.info(f"チャットログを更新しました。チャットID: {updated_record.id}, 更新内容: {updates_dict}")

    updated_chatlog_dto = ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=1,
    )

    return updated_chatlog_dto


@router.delete("/delete/chat/{chat_id}", response_model=dict, tags=["chat_delete"])
async def delete_chatlog(
    chat_id: int,
    engine: Annotated[Engine, Depends(get_engine)],
) -> dict[str, str]:
    logger.info(f"チャットログ削除リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    await delete_record(engine, ChatLogDemo, conditions)

    logger.info(f"チャットログを削除しました。チャットID: {chat_id}")

    return {"message": "チャットログが削除されました"}
