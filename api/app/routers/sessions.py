from datetime import datetime

from fastapi import APIRouter, Depends

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.session_dtos import (
    SessionDTO,
    SessionOrderBy,
    SessionSearchDTO,
    SessionUpdateDTO,
)
from api.app.models import Session, User
from api.app.security.role import Role, role_required
from api.app.security.jwt_token import get_current_user
from api.logger import getLogger

router = APIRouter()
logger = getLogger("session_router")


@router.get("/create_session", response_model=SessionDTO)
@role_required(Role.STUDENT)
async def create_session(
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    """
    デフォルトのセッションを作成する GET メソッド。
    """
    logger.info(f"セッション作成リクエストを受け付けました。ユーザーID: {current_user.id}")

    # デフォルト値を設定してセッションを作成
    session_data = Session(
        session_name="Default Session",  # デフォルト値
        pub_data=datetime.now(),
        user_id=current_user.id,
    )
    # データベースにレコードを登録
    async with DBSession(engine) as db:
        db.add(session_data)
        await db.commit()
        await db.refresh(session_data)

    logger.info("新しいセッションを登録しました。")
    logger.info(f"セッションID:{session_data.id}")
    logger.info(f"セッション名:{session_data.session_name}")
    logger.info(f"投稿日時:{session_data.pub_data}")
    logger.info(f"ユーザーID:{session_data.user_id}")

    # DTO に変換して返却
    session_dto = SessionDTO(
        id=session_data.id,
        session_name=session_data.session_name,
        pub_data=session_data.pub_data,
        user_id=session_data.user_id,
    )
    return session_dto


@router.get("/view/session/", response_model=list[SessionDTO], tags=["session_get"])
@role_required(Role.STUDENT)
async def view_session(
    search_params: SessionSearchDTO = Depends(),
    order_by: SessionOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"セッション取得リクエストを受け付けました。検索条件: {search_params}")
    conditions = {}
    like_conditions = {}

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

    session_dto_list = [
        SessionDTO(
            id=session.id,
            session_name=session.session_name,
            pub_data=session.pub_data,
            user_id=session.user_id,
        )
        for session in sessions
    ]

    return session_dto_list


@router.put(
    "/update/session/{session_id}/", response_model=SessionDTO, tags=["session_put"]
)
@role_required(Role.STUDENT)
async def update_session(
    session_id: int,
    updates: SessionUpdateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"セッション更新リクエストを受け付けました。セッションID: {session_id}")
    conditions = {"id": session_id}
    updates_dict = updates.model_dump(
        exclude_unset=True
    )  # 送信されていないフィールドは無視
    updated_record = await update_record(engine, Session, conditions, updates_dict)

    logger.info(
        f"セッションを更新しました。セッションID: {updated_record.id}, 更新内容: {updates_dict}"
    )

    updated_session_dto = SessionDTO(
        id=updated_record.id,
        session_name=updated_record.session_name,
        pub_data=updated_record.pub_data,
        user_id=updated_record.user_id,
    )

    return updated_session_dto


@router.delete(
    "/delete/session/{session_id}/", response_model=dict, tags=["session_delete"]
)
@role_required(Role.STUDENT)
async def delete_session(
    session_id: int,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"セッション削除リクエストを受け付けました。セッションID: {session_id}")
    conditions = {"id": session_id}

    result = await delete_record(engine, Session, conditions)
    logger.info(f"セッションを削除しました。セッションID: {session_id}")

    return result
