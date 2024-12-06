from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.user_dtos import (
    UserCreateDTO,
    UserDTO,
    UserOrderBy,
    UserSearchDTO,
    UserUpdateDTO,
)
from api.app.models import User
from api.app.security.jwt_token import get_current_user, get_password_hash
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("user_router")


@router.post("/input/user/", response_model=UserDTO, tags=["user_post"])
@role_required(Role.ADMIN)
async def create_user(
    user: UserCreateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserDTO:
    """
    新しいユーザーを作成するエンドポイント。

    Args:
        user (UserCreateDTO): 作成するユーザー情報。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        UserDTO: 作成されたユーザー情報。
    """
    logger.info("ユーザー作成リクエストを受け付けました。")

    # 既存のメールアドレスのチェック
    existing_user = engine.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        logger.error(f"既に登録済みのメールアドレス: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user.password)

    # 新しいユーザーを作成
    user_data = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        authority=user.authority,
        major=user.major,
        pub_data=datetime.now(),
    )
    await add_db_record(engine, user_data)

    logger.info(f"新しいユーザーが作成されました。ユーザーID: {user_data.id}")

    return UserDTO(
        id=user_data.id,
        name=user_data.name,
        email=user_data.email,
        authority=user_data.authority,
        major=user_data.major,
    )


@router.get("/user/me", response_model=UserDTO, tags=["user_get"])
@role_required(Role.ADMIN)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserDTO:
    """
    現在のユーザー情報を取得するエンドポイント。

    Args:
        current_user (User): 現在認証されているユーザー。

    Returns:
        UserDTO: 現在のユーザー情報。
    """
    logger.info(f"現在のユーザー情報を取得: {current_user.email}")
    return UserDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        authority=current_user.authority,
        major=current_user.major,
    )


@router.get("/view/user/", response_model=list[UserDTO], tags=["user_get"])
@role_required(Role.ADMIN)
async def view_user(
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    search_params: Annotated[UserSearchDTO, Depends()],
    order_by: UserOrderBy | None = None,
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserDTO]:
    """
    ユーザーの検索と取得を行うエンドポイント。

    Args:
        search_params (UserSearchDTO): 検索条件。
        order_by (UserOrderBy | None): 並び順。
        limit (int | None): 最大取得件数。
        offset (int): スキップ件数。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        List[UserDTO]: ユーザー情報のリスト。
    """
    logger.info(f"ユーザー一覧の取得リクエストを受け付けました。検索条件: {search_params}")

    conditions, like_conditions = {}, {}
    if search_params.name:
        conditions["name"] = search_params.name
    if search_params.name_like:
        like_conditions["name"] = search_params.name_like
    if search_params.email:
        conditions["email"] = search_params.email
    if search_params.authority:
        conditions["authority"] = search_params.authority
    if search_params.major_like:
        like_conditions["major"] = search_params.major_like

    users = await select_table(
        engine,
        User,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"ユーザー一覧取得完了: {len(users)}件")

    return [
        UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            authority=user.authority,
            major=user.major,
        )
        for user in users
    ]


@router.put("/update/user/{user_id}/", response_model=UserDTO, tags=["user_put"])
@role_required(Role.ADMIN)
async def update_user(
    user_id: str,
    updates: UserUpdateDTO,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserDTO:
    """
    ユーザーを更新するエンドポイント。

    Args:
        user_id (str): 更新対象のユーザーID。
        updates (UserUpdateDTO): 更新内容。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        UserDTO: 更新されたユーザー情報。
    """
    logger.info(f"ユーザー更新リクエストを受け付けました。ユーザーID: {user_id}")

    updates_dict = updates.model_dump(exclude_unset=True)

    if "email" in updates_dict:
        existing_user = engine.exec(select(User).where(User.email == updates_dict["email"], User.id != user_id)).first()
        if existing_user:
            logger.info(f"既に登録済みのメールアドレス: {updates_dict['email']}")
            raise HTTPException(status_code=400, detail="Email already registered")

    if "password" in updates_dict:
        updates_dict["password"] = get_password_hash(updates_dict["password"])

    conditions = {"id": user_id}
    updated_record = await update_record(engine, User, conditions, updates_dict)

    logger.info(f"ユーザー情報を更新しました。ユーザーID: {updated_record.id}")

    return UserDTO(
        id=updated_record.id,
        name=updated_record.name,
        email=updated_record.email,
        authority=updated_record.authority,
        major=updated_record.major,
    )


@router.delete("/delete/user/{user_id}/", response_model=dict, tags=["user_delete"])
@role_required(Role.ADMIN)
async def delete_user(
    user_id: str,
    response: Response,
    engine: Annotated[Session, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """
    ユーザーを削除するエンドポイント。

    Args:
        user_id (str): 削除対象のユーザーID。
        response (Response): HTTPレスポンス。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        dict[str, str]: 削除メッセージ。
    """
    logger.info(f"ユーザー削除リクエスト: {user_id}")

    conditions = {"id": user_id}
    await delete_record(engine, User, conditions)

    if current_user.id == user_id:
        response.delete_cookie("access_token")
        logger.info("ログイン中のユーザーが削除されました。ログアウト処理を実行します。")
        return {"message": "User deleted and logged out successfully."}

    logger.info(f"ユーザー削除完了: {user_id}")
    return {"message": "User deleted successfully"}
