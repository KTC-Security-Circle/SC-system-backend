from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from api.app.models import SchoolInfo
from api.app.dtos.school_info_dtos import (
    SchoolInfoCreateDTO,
    SchoolInfoDTO,
    SchoolInfoSearchDTO,
    SchoolInfoUpdateDTO,
)
from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.security.role import Role, role_required
from api.app.security.jwt_token import get_current_user
from api.logger import getLogger
import logging


router = APIRouter()
logger = getLogger("schoolinfo_router")
logger.setLevel(logging.DEBUG)

@router.post("/input/schoolinfo/", response_model=SchoolInfoDTO, tags=["schoolinfo_post"])
@role_required(Role.STAFF)
async def create_school_info(
    school_info: SchoolInfoCreateDTO,
    engine=Depends(get_engine),
    current_user=Depends(get_current_user),
):
    logger.info(f"学校情報作成リクエスト。ユーザー: {current_user.id}")
    new_school_info = SchoolInfo(
        contents=school_info.contents,
        pub_date=school_info.pub_date or datetime.now(),
        updated_at=school_info.updated_at or datetime.now(),
        created_by=current_user.id,
    )
    await add_db_record(engine, new_school_info)
    logger.info(f"新しい学校情報が作成されました。ID: {new_school_info.id}")
    return new_school_info


@router.get("/view/schoolinfo/", response_model=list[SchoolInfoDTO], tags=["schoolinfo_get"])
@role_required(Role.STAFF)
async def view_school_info(
    search_params: SchoolInfoSearchDTO = Depends(),
    limit: int | None = None,
    offset: int | None = 0,
    engine=Depends(get_engine),
    current_user=Depends(get_current_user),
):
    logger.info(f"学校情報一覧取得リクエスト: {search_params}")
    conditions = {}
    like_conditions = {}

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
            contents=info.contents,
            pub_date=info.pub_date,
            updated_at=info.updated_at,
            created_by=info.created_by,
        )
        for info in school_infos
    ]


@router.put("/update/schoolinfo/{school_info_id}/", response_model=SchoolInfoDTO, tags=["schoolinfo_put"])
@role_required(Role.STAFF)
async def update_school_info(
    school_info_id: int,
    updates: SchoolInfoUpdateDTO,
    engine=Depends(get_engine),
    current_user=Depends(get_current_user),
):
    logger.info(f"学校情報更新リクエスト: {school_info_id}")
    updates_dict = updates.model_dump(exclude_unset=True)

    conditions = {"id": school_info_id}
    updated_record = await update_record(engine, SchoolInfo, conditions, updates_dict)
    logger.info(f"学校情報を更新しました。ID: {updated_record.id}")
    return SchoolInfoDTO(
        id=updated_record.id,
        contents=updated_record.contents,
        pub_date=updated_record.pub_date,
        updated_at=updated_record.updated_at,
        created_by=updated_record.created_by,
    )


@router.delete("/delete/schoolinfo/{school_info_id}/", response_model=dict, tags=["schoolinfo_delete"])
@role_required(Role.STAFF)
async def delete_school_info(
    school_info_id: int,
    engine=Depends(get_engine),
    current_user=Depends(get_current_user),
):
    logger.info(f"学校情報削除リクエスト: {school_info_id}")
    conditions = {"id": school_info_id}
    result = await delete_record(engine, SchoolInfo, conditions)
    logger.info(f"学校情報を削除しました。ID: {school_info_id}")
    return {"message": "SchoolInfo deleted successfully"}
