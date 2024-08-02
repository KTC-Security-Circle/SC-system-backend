from fastapi import APIRouter, Depends
from datetime import datetime
from api.app.models import Sessions  # SQLModelモデルをインポート
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from typing import Optional
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/session/", response_model=Sessions)
async def create_sessions(session: Sessions, engine=Depends(get_engine)):
    session_data = Sessions(
        id=session.id,
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=session.user_id,
    )
    await add_db_record(engine, session_data)
    logger.info("新しいセッションを登録します。")
    logger.info(f"セッションID:{session.id}")
    logger.info(f"セッション名:{session.session_name}")
    logger.info(f"投稿日時:{session.pub_data}")
    logger.info(f"ユーザーID:{session.user_id}")
    return session_data


@router.get("/app/view/session/", response_model=list[Sessions])
async def view_sessions(
    limit: Optional[int] = None, offset: Optional[int] = 0, engine=Depends(get_engine)
):
    sessions = await select_table(engine, Sessions, offset, limit)
    logger.debug(sessions)
    return sessions


@router.put("/app/update/session/{session_id}/", response_model=Sessions)
async def update_sessions(
    session_id: int, updates: dict[str, str], engine=Depends(get_engine)
):
    conditions = {"id": session_id}
    updated_record = await update_record(engine, Sessions, conditions, updates)
    return updated_record


@router.delete("/app/delete/session/{session_id}/", response_model=dict)
async def delete_session(session_id: int, engine=Depends(get_engine)):
    conditions = {"id": session_id}
    result = await delete_record(engine, Sessions, conditions)
    return result
