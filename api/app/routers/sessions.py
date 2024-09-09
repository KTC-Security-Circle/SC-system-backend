from fastapi import APIRouter, Depends
from datetime import datetime
from api.app.models import User, Session
from api.app.dtos.session_dtos import (
    SessionDTO,
    SessionCreateDTO,
    SessionOrderBy,
    SessionSearchDTO,
    SessionUpdateDTO
)
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user
from api.app.role import Role, role_required
from typing import Optional
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/session/", response_model=SessionDTO, tags=["session_post"])
@role_required(Role.ADMIN)
async def create_session(
    session: SessionCreateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
    ):
    session_data = Session(
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=current_user.id,  # 現在のユーザーIDを使用
    )
    await add_db_record(engine, session_data)
    logger.info("新しいセッションを登録します。")
    logger.info(f"セッションID:{session_data.id}")
    logger.info(f"セッション名:{session_data.session_name}")
    logger.info(f"投稿日時:{session_data.pub_data}")
    logger.info(f"ユーザーID:{session_data.user_id}")
    session_dto = SessionDTO(
        id=session_data.id,
        session_name=session_data.session_name,
        pub_data=session_data.pub_data,
        user_id=session_data.user_id
    )
    return session_dto


@router.get("/app/view/session/", response_model=list[SessionDTO], tags=["session_get"])
@role_required(Role.ADMIN)  # admin権限が必要
async def view_session(
    search_params: SessionSearchDTO = Depends(),
    order_by: Optional[SessionOrderBy] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
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
        order_by=order_by
    )

    logger.debug(sessions)

    session_dto_list = [
        SessionDTO(
            id=session.id,
            session_name=session.session_name,
            pub_data=session.pub_data,
            user_id=session.user_id
        )
        for session in sessions
    ]

    return session_dto_list


@router.put("/app/update/session/{session_id}/", response_model=SessionDTO, tags=["session_put"])
@role_required(Role.ADMIN)
async def update_session(
    session_id: int,
    updates: SessionUpdateDTO,  # DTOを使用
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    conditions = {"id": session_id}
    updates_dict = updates.model_dump(exclude_unset=True)  # 送信されていないフィールドは無視
    updated_record = await update_record(engine, Session, conditions, updates_dict)

    updated_session_dto = SessionDTO(
        id=updated_record.id,
        session_name=updated_record.session_name,
        pub_data=updated_record.pub_data,
        user_id=updated_record.user_id
    )

    return updated_session_dto


@router.delete("/app/delete/session/{session_id}/", response_model=dict, tags=["session_delete"])
@role_required(Role.ADMIN)  # admin権限が必要
async def delete_session(
    session_id: int,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    # 削除対象のセッションを取得
    conditions = {"id": session_id}
    # session_to_delete = await select_table(engine, Session, conditions)

    # if not session_to_delete:
    #     raise HTTPException(status_code=404, detail="セッションが見つかりません")

    # # セッションが現在のユーザーによって作成されたかを確認
    # if session_to_delete[0].user_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="このセッションを削除する権限がありません")

    # 削除を実行
    result = await delete_record(engine, Session, conditions)
    return result
