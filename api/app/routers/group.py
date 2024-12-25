import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.group_dtos import (
    GroupCreateDTO,
    GroupDTO,
    GroupOrderBy,
    GroupSearchDTO,
    GroupUpdateDTO,
)
from api.app.models import Group, User
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("group_router", logging.DEBUG)


@router.post("/input/group/", response_model=GroupDTO, tags=["group_post"])
@role_required(Role.ADMIN)
async def create_group(
    group: GroupCreateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GroupDTO:
    """
    グループを作成するエンドポイント。

    Args:
        group (GroupCreateDTO): 作成するグループのデータ。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        GroupDTO: 作成されたグループのデータ。
    """
    logger.info(f"グループ作成リクエストを受け付けました。ユーザー: {current_user.id}")

    # グループ名の重複チェック
    existing_group = engine.exec(select(Group).where(Group.name == group.name)).first()
    if existing_group:
        logger.error(f"既に存在するグループ名: {group.name}")
        raise HTTPException(status_code=400, detail="Group name already exists")

    # 新しいグループ作成
    new_group = Group(name=group.name, description=group.description)
    await add_db_record(engine, new_group)

    logger.info(f"新しいグループが作成されました。グループID: {new_group.id}")
    return GroupDTO(
        id=new_group.id,
        name=new_group.name,
        description=new_group.description,
    )


@router.get("/view/group/", response_model=list[GroupDTO], tags=["group_get"])
@role_required(Role.ADMIN)
async def view_groups(
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    search_params: Annotated[GroupSearchDTO, Depends()],
    order_by: GroupOrderBy | None = None,
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[GroupDTO]:
    """
    グループを検索し一覧を取得するエンドポイント。

    Args:
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。
        search_params (GroupSearchDTO): 検索条件。
        order_by (GroupOrderBy | None): 並び順。
        limit (int | None): 最大取得件数。
        offset (int): スキップする件数。

    Returns:
        list[GroupDTO]: グループのリスト。
    """
    logger.info(f"グループ一覧取得リクエスト。検索条件: {search_params}")
    conditions, like_conditions = {}, {}

    # 検索条件をDTOから適用
    if search_params.name:
        conditions["name"] = search_params.name
    if search_params.name_like:
        like_conditions["name"] = search_params.name_like
    if search_params.description_like:
        like_conditions["description"] = search_params.description_like

    groups = await select_table(
        engine,
        Group,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"グループ一覧取得成功: {len(groups)}件")
    return [GroupDTO(id=group.id, name=group.name, description=group.description) for group in groups]


@router.put("/update/group/{group_id}/", response_model=GroupDTO, tags=["group_put"])
@role_required(Role.ADMIN)
async def update_group(
    group_id: int,
    updates: GroupUpdateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GroupDTO:
    """
    グループを更新するエンドポイント。

    Args:
        group_id (int): 更新対象のグループID。
        updates (GroupUpdateDTO): 更新内容。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        GroupDTO: 更新されたグループのデータ。
    """
    logger.info(f"グループ更新リクエスト: {group_id}")

    # グループの取得と存在確認
    group = engine.get(Group, group_id)
    if not group:
        logger.error(f"グループが見つかりません: {group_id}")
        raise HTTPException(status_code=404, detail="Group not found")

    # グループ名の重複チェック
    updates_dict = updates.model_dump(exclude_unset=True)
    if "name" in updates_dict:
        existing_group = engine.exec(
            select(Group).where(Group.name == updates_dict["name"], Group.id != group_id)
        ).first()
        if existing_group:
            logger.error(f"既に存在するグループ名: {updates_dict['name']}")
            raise HTTPException(status_code=400, detail="Group name already exists")

    # グループの更新
    conditions = {"id": group_id}
    updated_record = await update_record(engine, Group, conditions, updates_dict)

    logger.info(f"グループ情報を更新しました: {updated_record.id}")
    return GroupDTO(
        id=updated_record.id,
        name=updated_record.name,
        description=updated_record.description,
    )


@router.delete("/delete/group/{group_id}/", response_model=dict, tags=["group_delete"])
@role_required(Role.ADMIN)
async def delete_group(
    group_id: int,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    グループを削除するエンドポイント。

    Args:
        group_id (int): 削除対象のグループID。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        dict[str, str]: 削除完了メッセージ。
    """
    logger.info(f"グループ削除リクエスト: {group_id}")

    # グループの存在確認
    group = engine.get(Group, group_id)
    if not group:
        logger.error(f"グループが見つかりません: {group_id}")
        raise HTTPException(status_code=404, detail="Group not found")

    # グループの削除
    conditions = {"id": group_id}
    await delete_record(engine, Group, conditions)
    logger.info(f"グループを削除しました: {group_id}")

    return {"message": "Group deleted successfully"}
