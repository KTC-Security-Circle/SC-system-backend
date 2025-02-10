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
from api.app.dtos.world_dtos import (
    WorldCreateDTO,
    WorldDTO,
    WorldOrderBy,
    WorldSearchDTO,
    WorldUpdateDTO,
)
from api.app.models import World
from api.app.security.jwt_token import get_current_user, get_password_hash
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("world_router")


@router.get("/view/world", response_model=list[WorldDTO], tags=["world_get"])
@role_required(Role.ADMIN)
async def view_world(
    search_params: Annotated[WorldSearchDTO, Depends()],
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[World, Depends(get_current_user)],
    order_by: WorldOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
) -> list[WorldDTO]:
    logger.info(
        f"ユーザー一覧の取得リクエストを受け付けました。検索条件: {search_params}"
    )
    conditions = {}
    like_conditions = {}

    # 検索条件をDTOから適用
    if search_params.name:
        conditions["name"] = search_params.name

    if search_params.name_like:
        like_conditions["name"] = search_params.name_like

    worlds = await select_table(
        engine,
        World,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"ユーザー一覧取得完了: {len(worlds)}件")

    world_dto_list = [
        WorldDTO(
            id=world.id,
            name=world.name,
        )
        for world in worlds
    ]

    return world_dto_list
