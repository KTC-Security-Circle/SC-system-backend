import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from sc_system_ai.template.azure_cosmos import CosmosDBManager

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.school_info_dtos import (
    SchoolInfoCreateDTO,
    SchoolInfoDTO,
    SchoolInfoSearchDTO,
    SchoolInfoUpdateDTO,
    SchoolInfoTitleDTO,
)
from api.app.models import SchoolInfo, User
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("schoolinfo_router", logging.DEBUG)

@router.post("/input/schoolinfo/", response_model=SchoolInfoDTO, tags=["schoolinfo_post"])
@role_required(Role.STAFF)
async def create_school_info(
    school_info: SchoolInfoCreateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SchoolInfoDTO:
    """
    学校情報を作成するエンドポイント。

    Args:
        school_info (SchoolInfoCreateDTO): 学校情報のデータ。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        SchoolInfoDTO: 作成された学校情報。
    """
    logger.info(f"学校情報作成リクエスト。ユーザー: {current_user.id}")

    new_school_info = SchoolInfo(
        title=school_info.title,
        contents=school_info.contents,
        pub_date=school_info.pub_date or datetime.now(),
        updated_at=school_info.updated_at or datetime.now(),
        created_by=current_user.id,
    )
    await add_db_record(engine, new_school_info)

    logger.info(f"新しい学校情報が作成されました。ID: {new_school_info.id}")
    cosmos_manager = CosmosDBManager(create_container=True)

    cosmos_manager.create_document(
        text=new_school_info.contents,
        title=new_school_info.title,
        source_id=new_school_info.id,
    )

    logger.info(f"新しい学校情報が作成されました。ID: {new_school_info.id}")


    return SchoolInfoDTO(
        id=new_school_info.id,
        title=new_school_info.title,
        contents=new_school_info.contents,
        pub_date=new_school_info.pub_date,
        updated_at=new_school_info.updated_at,
        created_by=new_school_info.created_by,
    )


@router.get(
    "/view/schoolinfo/", response_model=list[SchoolInfoDTO], tags=["schoolinfo_get"]
)
@role_required(Role.STUDENT)
async def view_school_info(
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    search_params: Annotated[SchoolInfoSearchDTO, Depends()],
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SchoolInfoDTO]:
    """
    学校情報を検索して一覧を取得するエンドポイント。

    Args:
        search_params (SchoolInfoSearchDTO): 検索条件。
        limit (int | None): 最大取得件数。
        offset (int): スキップ件数。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        List[SchoolInfoDTO]: 学校情報のリスト。
    """
    logger.info(f"学校情報一覧取得リクエスト: {search_params}")
    conditions, like_conditions = {}, {}

    if search_params.title_like:
        like_conditions["title"] = search_params.title_like
    if search_params.contents_like:
        like_conditions["contents"] = search_params.contents_like
    if search_params.created_by:
        conditions["created_by"] = search_params.created_by

    school_infos = await select_table(
        engine,
        SchoolInfo,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
    )

    logger.info(f"学校情報一覧取得成功: {len(school_infos)}件")
    return [
        SchoolInfoDTO(
            id=info.id,
            title=info.title,
            contents=info.contents,
            pub_date=info.pub_date,
            updated_at=info.updated_at,
            created_by=info.created_by,
        )
        for info in school_infos
    ]


@router.get(
    "/view/schoolinfo/title",
    response_model=list[SchoolInfoTitleDTO],
    tags=["schoolinfo_get"],
)

@role_required(Role.STUDENT)
async def view_school_info_title(
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    search_params: Annotated[SchoolInfoSearchDTO, Depends()],
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SchoolInfoTitleDTO]:
    """
    学校情報を検索して一覧を取得するエンドポイント。

    Args:
        search_params (SchoolInfoSearchDTO): 検索条件。
        limit (int | None): 最大取得件数。
        offset (int): スキップ件数。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        List[SchoolInfoTitleDTO]: 学校情報のリスト。
    """
    logger.info(f"学校情報一覧取得リクエスト: {search_params}")
    conditions, like_conditions = {}, {}

    if search_params.title_like:
        like_conditions["title"] = search_params.title_like
    if search_params.contents_like:
        like_conditions["contents"] = search_params.contents_like
    if search_params.created_by:
        conditions["created_by"] = search_params.created_by
    if search_params.title_like:
        like_conditions["title"] = search_params.title_like

    school_infos = await select_table(
        engine,
        SchoolInfo,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
    )

    logger.info(f"学校情報一覧取得成功: {len(school_infos)}件")
    return [
        SchoolInfoTitleDTO(
            id=info.id,
            title=info.title,
        )
        for info in school_infos
    ]


@router.put("/update/schoolinfo/{school_info_id}/", response_model=SchoolInfoDTO, tags=["schoolinfo_put"])
@role_required(Role.STAFF)
async def update_school_info(
    school_info_id: int,
    updates: SchoolInfoUpdateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SchoolInfoDTO:
    """
    学校情報を更新するエンドポイント。

    Args:
        school_info_id (int): 更新対象の学校情報ID。
        updates (SchoolInfoUpdateDTO): 更新内容。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        SchoolInfoDTO: 更新された学校情報。
    """
    logger.info(f"学校情報更新リクエスト: {school_info_id}")
    updates_dict = updates.model_dump(exclude_unset=True)

    conditions = {"id": school_info_id}
    # TODO: ベクターデータベースの情報を更新するか、削除してから再作成する
    updated_record = await update_record(engine, SchoolInfo, conditions, updates_dict)

    cosmos_manager = CosmosDBManager(create_container=True)

    cosmos_manager.update_document(
        text=updated_record.contents,
        text_type='markdown',
        title=updated_record.title,
        source_id=updated_record.id,
    )

    logger.info(f"学校情報を更新しました。ID: {updated_record.id}")
    return SchoolInfoDTO(
        id=updated_record.id,
        title=updated_record.title,
        contents=updated_record.contents,
        pub_date=updated_record.pub_date,
        updated_at=updated_record.updated_at,
        created_by=updated_record.created_by,
    )


@router.delete("/delete/schoolinfo/{school_info_id}/", response_model=dict, tags=["schoolinfo_delete"])
@role_required(Role.STAFF)
async def delete_school_info(
    school_info_id: int,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    学校情報を削除するエンドポイント。

    Args:
        school_info_id (int): 削除対象の学校情報ID。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        dict[str, str]: 削除完了メッセージ。
    """
    logger.info(f"学校情報削除リクエスト: {school_info_id}")

    conditions = {"id": school_info_id}
    # TODO: ベクターデータベースから情報を削除する
    await delete_record(engine, SchoolInfo, conditions)

    logger.info(f"学校情報を削除しました。ID: {school_info_id}")
    return {"message": "SchoolInfo deleted successfully"}
