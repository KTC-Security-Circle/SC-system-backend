import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.session_dtos import (
    SessionCreateDTO,
    SessionDTO,
    SessionOrderBy,
    SessionSearchDTO,
    SessionUpdateDTO,
)
from api.app.models import Session, User
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("session_router", logging.DEBUG)

@router.post("/input/session/", response_model=SessionDTO, tags=["session_post"])
@role_required(Role.STUDENT)
async def create_session(
    session: SessionCreateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SessionDTO:
    """
    新しいセッションを作成するエンドポイント。

    Args:
        session (SessionCreateDTO): 作成するセッションのデータ。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        SessionDTO: 作成されたセッションのデータ。
    """
    logger.info(f"セッション作成リクエストを受け付けました。ユーザーID: {current_user.id}")

    session_data = Session(
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=current_user.id,
    )
    await add_db_record(engine, session_data)

    logger.info(f"新しいセッションが作成されました。セッションID: {session_data.id}")

    return SessionDTO(
        id=session_data.id,
        session_name=session_data.session_name,
        pub_data=session_data.pub_data,
        user_id=session_data.user_id,
    )


@router.get("/view/session/", response_model=list[SessionDTO], tags=["session_get"])
@role_required(Role.STUDENT)
async def view_session(
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    search_params: Annotated[SessionSearchDTO, Depends()],
    order_by: SessionOrderBy | None = None,
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SessionDTO]:
    """
    セッションの検索と取得を行うエンドポイント。

    Args:
        search_params (SessionSearchDTO): 検索条件。
        order_by (SessionOrderBy | None): 並び順。
        limit (int | None): 最大取得件数。
        offset (int): スキップする件数。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        List[SessionDTO]: セッションのリスト。
    """
    logger.info(f"セッション取得リクエストを受け付けました。検索条件: {search_params}")

    conditions, like_conditions = {}, {}

    if search_params.session_name:
        conditions["session_name"] = search_params.session_name
    if search_params.session_name_like:
        like_conditions["session_name"] = search_params.session_name_like
    if search_params.user_id:
        conditions["user_id"] = search_params.user_id

    sessions = await select_table(
        engine,
        Session,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"セッション取得完了: {len(sessions)}件")

    return [
        SessionDTO(
            id=session.id,
            session_name=session.session_name,
            pub_data=session.pub_data,
            user_id=session.user_id,
        )
        for session in sessions
    ]


@router.put("/update/session/{session_id}/", response_model=SessionDTO, tags=["session_put"])
@role_required(Role.STUDENT)
async def update_session(
    session_id: int,
    updates: SessionUpdateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SessionDTO:
    """
    セッションを更新するエンドポイント。

    Args:
        session_id (int): 更新対象のセッションID。
        updates (SessionUpdateDTO): 更新内容。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        SessionDTO: 更新後のセッションデータ。
    """
    logger.info(f"セッション更新リクエストを受け付けました。セッションID: {session_id}")

    conditions = {"id": session_id}
    updates_dict = updates.model_dump(exclude_unset=True)

    updated_record = await update_record(engine, Session, conditions, updates_dict)

    logger.info(f"セッションを更新しました。セッションID: {updated_record.id}")

    return SessionDTO(
        id=updated_record.id,
        session_name=updated_record.session_name,
        pub_data=updated_record.pub_data,
        user_id=updated_record.user_id,
    )


@router.delete("/delete/session/{session_id}/", response_model=dict, tags=["session_delete"])
@role_required(Role.STUDENT)
async def delete_session(
    session_id: int,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    セッションを削除するエンドポイント。

    Args:
        session_id (int): 削除対象のセッションID。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        dict[str, str]: 削除完了メッセージ。
    """
    logger.info(f"セッション削除リクエストを受け付けました。セッションID: {session_id}")

    conditions = {"id": session_id}
    await delete_record(engine, Session, conditions)

    logger.info(f"セッションを削除しました。セッションID: {session_id}")

    return {"message": "Session deleted successfully"}
