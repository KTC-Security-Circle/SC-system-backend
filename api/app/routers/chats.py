from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from api.app.models import Users, ChatLog  # SQLModelモデルをインポート
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user
from typing import Optional, List
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/chat/", response_model=ChatLog, tags=["chat_post"])
async def create_chatlog(
    chatlog: ChatLog,
    engine=Depends(get_engine)
):
    chat_log_data = ChatLog(
        id=chatlog.id,
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=datetime.now(),
        session_id=chatlog.session_id,
    )
    await add_db_record(engine, chat_log_data)
    logger.info("新しいチャットを登録します。")
    logger.info(f"チャットID:{chatlog.id}")
    logger.info(f"チャット内容:{chatlog.message}")
    logger.info(f"ボットの返信:{chatlog.bot_reply}")
    logger.info(f"投稿日時:{chatlog.pub_data}")
    logger.info(f"セッションID:{chatlog.session_id}")
    return chat_log_data


@router.get("/app/view/chat/", response_model=List[ChatLog], tags=["chat_get"])
async def view_chatlog(
    session_id: Optional[int] = Query(None, description="セッションIDでフィルタリング"),
    limit: Optional[int] = Query(10, description="取得するレコードの数"),
    offset: Optional[int] = Query(0, description="取得するレコードの開始位置"),
    engine=Depends(get_engine)
):
    conditions_dict = {}
    if session_id is not None:
        conditions_dict["session_id"] = session_id

    chatlog = await select_table(engine, ChatLog, conditions_dict, offset=offset, limit=limit)
    logger.debug(chatlog)
    return chatlog


@router.put("/app/update/chat/{chat_id}/", response_model=ChatLog, tags=["chat_put"])
async def update_chatlog(
    chat_id: int,
    updates: dict[str, str],
    engine=Depends(get_engine)
):
    conditions = {"id": chat_id}
    updated_record = await update_record(engine, ChatLog, conditions, updates)
    return updated_record


@router.delete("/app/delete/chat/{chat_id}/", response_model=dict, tags=["chat_delete"])
async def delete_chatlog(
    chat_id: int,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {"id": chat_id}
    result = await delete_record(engine, ChatLog, conditions)
    return result
