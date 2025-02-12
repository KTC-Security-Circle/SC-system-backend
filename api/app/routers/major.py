from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import Engine
from sqlmodel import Session, select

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.major_dtos import (
    MajorCreateDTO,
    MajorDTO,
    MajorOrderBy,
    MajorSearchDTO,
    MajorUpdateDTO,
)
from api.app.models import Major
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("major_router")


@router.post("/input/major", response_model=MajorDTO, tags=["major_post"])
@role_required(Role.ADMIN)
async def create_major(
    major: MajorCreateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[Major, Depends(get_current_user)],
) -> MajorDTO:

    # 新しいユーザーオブジェクトを作成
    major_data = Major(
        name=major.name,
        world_id=major.world_id,
        pub_data=datetime.now(),
    )

    # データベースにレコードを追加
    await add_db_record(engine, major_data)

    # MajorDTO を作成して返す
    major_dto = MajorDTO(
        id=major_data.id,
        name=major_data.name,
        world_id=major.world_id
    )

    return major_dto


@router.get("/view/major", response_model=list[MajorDTO], tags=["major_get"])
@role_required(Role.ADMIN)
async def view_major(
    search_params: Annotated[MajorSearchDTO, Depends()],
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[Major, Depends(get_current_user)],
    order_by: MajorOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
) -> list[MajorDTO]:
    logger.info(
        f"ユーザー一覧の取得リクエストを受け付けました。検索条件: {search_params}"
    )
    conditions = {}
    like_conditions = {}

    # 検索条件をDTOから適用
    if search_params.name:
        conditions["name"] = search_params.name

    if search_params.world_id:
        conditions["world_id"] = search_params.world_id

    if search_params.name_like:
        like_conditions["name"] = search_params.name_like

    majors = await select_table(
        engine,
        Major,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"ユーザー一覧取得完了: {len(majors)}件")

    major_dto_list = [
        MajorDTO(
            id=major.id,
            name=major.name,
            world_id=major.world_id
        )
        for major in majors
    ]

    return major_dto_list
