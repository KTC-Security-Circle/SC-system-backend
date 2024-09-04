from fastapi import APIRouter, Depends
from api.app.models import Users  # SQLModelモデルをインポート
from api.app.dto import UserDTO
from api.app.database.database import (
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
)
from api.app.security.jwt_token import get_current_user, get_password_hash
from typing import Optional
from api.logger import getLogger
from api.app.role import Role, role_required
from pydantic import EmailStr

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/user/", response_model=UserDTO, tags=["users_post"])
@role_required(Role.ADMIN)
async def create_users(
    user: Users,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    hashed_password = get_password_hash(user.password)
    user_data = Users(
        name=user.name,
        email=user.email,
        password=hashed_password,  # ここでパスワードがハッシュされていることを確認
        authority=user.authority,
    )
    await add_db_record(engine, user_data)
    logger.info("新しいユーザーを登録します。")
    logger.info(f"ユーザーID:{user.id}")
    logger.info(f"ユーザー名:{user.name}")
    logger.info(f"E-mail:{user.email}")
    logger.info(f"権限情報:{user.authority}")

    user_dto = UserDTO(
        id=user_data.id,
        name=user_data.name,
        email=user_data.email,
        authority=user_data.authority
    )
    return user_dto


@router.get("/user/me", response_model=UserDTO, tags=["users_get"])
@role_required(Role.ADMIN)
async def get_me(current_user: Users = Depends(get_current_user)):
    me_dto = UserDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        authority=current_user.authority
    )
    return me_dto


@router.get("/app/view/user/", response_model=list[UserDTO], tags=["users_get"])
@role_required(Role.ADMIN)  # admin権限が必要
async def view_users(
    name: Optional[str] = None,
    name_like: Optional[str] = None,  # 名前の部分一致フィルタ
    email: Optional[EmailStr] = None,
    order_by: Optional[str] = None,  # ソート基準のフィールド名
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    conditions = {}
    like_conditions = {}

    if name:
        conditions["name"] = name

    if name_like:
        like_conditions["name"] = name_like

    if email:
        conditions["email"] = email

    users = await select_table(
        engine,
        Users,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by
    )

    logger.debug(users)

    user_dto_list = [
        UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            authority=user.authority
        )
        for user in users
    ]

    return user_dto_list



@router.put("/app/update/user/{user_id}/", response_model=UserDTO, tags=["users_put"])
@role_required(Role.ADMIN)  # admin権限が必要
async def update_users(
    user_id: str,
    updates: dict[str, str],
    engine=Depends(get_engine),
    current_user: Users = Depends(get_current_user)
):
    if 'password' in updates:
        updates['password'] = get_password_hash(
            updates['password'])  # パスワードをハッシュ化
    conditions = {"id": user_id}
    updated_record = await update_record(engine, Users, conditions, updates)
    updated_user_dto = UserDTO(
        id=updated_record.id,
        name=updated_record.name,
        email=updated_record.email,
        authority=updated_record.authority
    )
    return updated_user_dto


@router.delete("/app/delete/user/{user_id}/", response_model=dict, tags=["users_delete"])
@role_required(Role.ADMIN)  # admin権限が必要
async def delete_user(
    user_id: str,
    engine=Depends(get_engine),
):
    conditions = {"id": user_id}
    result = await delete_record(engine, Users, conditions)
    return result
