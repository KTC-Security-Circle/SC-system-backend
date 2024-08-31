from fastapi import APIRouter, Depends
from api.app.models import Users  # SQLModelモデルをインポート
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user
from typing import Optional
from api.logger import getLogger

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/user/", response_model=Users, tags=["users_post"])
async def create_users(
    user: Users,
    engine=Depends(get_engine)
):
    user_data = Users(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        authority=user.authority,
    )
    await add_db_record(engine, user_data)
    logger.info("新しいユーザーを登録します。")
    logger.info(f"ユーザーID:{user.id}")
    logger.info(f"ユーザー名:{user.name}")
    logger.info(f"E-mail:{user.email}")
    logger.info(f"権限情報:{user.authority}")
    return user_data


@router.get("/app/view/user/", response_model=list[Users], tags=["users_get"])
async def view_users(
    conditions: Optional[dict] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine)
):
    users = await select_table(engine, Users, conditions, offset, limit)
    logger.debug(users)
    return users


@router.put("/app/update/user/{user_id}/", response_model=Users, tags=["users_put"])
async def update_users(
    user_id: int, updates: dict[str, str],
    engine=Depends(get_engine),
):
    conditions = {"id": user_id}
    updated_record = await update_record(engine, Users, conditions, updates)
    return updated_record


@router.delete("/app/delete/user/{user_id}/", response_model=dict, tags=["users_delete"])
async def delete_user(
    user_id: int,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {"id": user_id}
    result = await delete_record(engine, Users, conditions)
    return result
