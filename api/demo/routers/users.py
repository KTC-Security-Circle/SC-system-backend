from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine
from sqlmodel import Session, select

# from api.app.security.jwt_token import get_current_user, get_password_hash
from api.demo.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.demo.database.engine import get_engine
from api.demo.dtos.user_dtos import (
    UserCreateDTO,
    UserDTO,
    UserOrderBy,
    UserSearchDTO,
    UserUpdateDTO,
)
from api.demo.models import UserDemo
from api.logger import getLogger

router = APIRouter()
logger = getLogger("user_router")


@router.post("/input/user/", response_model=UserDTO, tags=["user_post"])
async def create_user(
    user: UserCreateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
) -> UserDTO:
    logger.info("ユーザー作成リクエストを受け付けました。")

    session = Session(engine)

    stmt = select(UserDemo).where(UserDemo.email == user.email)
    # 既存のメールアドレスのチェック
    existing_user = session.exec(stmt).first()

    if existing_user:
        session.close()
        logger.error(f"既に登録済みのメールアドレス: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    session.close()

    # パスワードをハッシュ化
    # hashed_password = get_password_hash(user.password)

    # 新しいユーザーオブジェクトを作成
    user_data = UserDemo(
        name=user.name,
        email=user.email,
        password=user.password,  # ハッシュ化されたパスワードを保存
        authority=user.authority,
        major=user.major,
        pub_data=datetime.now(),
    )

    # データベースにレコードを追加
    await add_db_record(engine, user_data)

    # ログに情報を出力
    logger.info("新しいユーザーが作成されました")
    logger.info(f"ユーザーID:{user_data.id}")
    logger.info(f"ユーザー名:{user_data.name}")
    logger.info(f"E-mail:{user_data.email}")
    logger.info(f"権限情報:{user_data.authority}")
    logger.info(f"専攻情報:{user_data.major}")

    # UserDTO を作成して返す
    user_dto = UserDTO(
        id=user_data.id,
        name=user_data.name,
        email=user_data.email,
        authority=user_data.authority,
        major=user_data.major,
    )

    return user_dto


@router.get("/user/me", response_model=UserDTO, tags=["user_get"])
async def get_me() -> UserDTO:
    try:
        logger.info("現在のユーザー情報を取得:")

        me_dto = UserDTO(
            id=1,
            name="Taro Yamada",
            email="taro.yamada@example.com",
            authority="admin",
            major="fugafuga専攻",
        )
        return me_dto

    except Exception as e:
        logger.error(f"ユーザー情報取得中にエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"ユーザー情報の取得中にエラーが発生しました。{str(e)}",
        ) from e


@router.get("/view/user/", response_model=list[UserDTO], tags=["user_get"])
async def view_user(
    search_params: Annotated[UserSearchDTO, Depends()],
    engine: Annotated[Engine, Depends(get_engine)],
    order_by: UserOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
) -> list[UserDTO]:
    logger.info(f"ユーザー一覧の取得リクエストを受け付けました。検索条件: {search_params}")
    conditions = {}
    like_conditions = {}

    # 検索条件をDTOから適用
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
        UserDemo,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"ユーザー一覧取得完了: {len(users)}件")

    user_dto_list = [
        UserDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            authority=user.authority,
            major=user.major,
        )
        for user in users
    ]

    return user_dto_list


@router.put("/update/user/{user_id}/", response_model=UserDTO, tags=["user_put"])
async def update_user(
    user_id: str,
    updates: UserUpdateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
) -> UserDTO:
    logger.info(f"ユーザー更新リクエストを受け付けました。ユーザーID: {user_id}")
    updates_dict = updates.model_dump(exclude_unset=True)

    session = Session(engine)

    # 既存のメールアドレスのチェック
    if "email" in updates_dict:
        existing_user = session.exec(select(UserDemo).where(UserDemo.email == updates_dict["email"])).first()

        if existing_user:
            session.close()
            logger.info(f"既に登録済みのメールアドレス: {updates_dict['email']}")
            raise HTTPException(status_code=400, detail="Email already registered")

    session.close()

    # パスワードのハッシュ化
    # if "password" in updates_dict:
    #     updates_dict["password"] = get_password_hash(updates_dict["password"])

    # 更新内容を辞書形式でupdate_record関数に渡す
    conditions = {"id": user_id}
    updated_record = await update_record(engine, UserDemo, conditions, updates_dict)
    logger.info(f"ユーザー情報を更新しました。ユーザーID: {updated_record.id}")
    updated_user_dto = UserDTO(
        id=updated_record.id,
        name=updated_record.name,
        email=updated_record.email,
        authority=updated_record.authority,
        major=updated_record.major,
    )
    return updated_user_dto


@router.delete("/delete/user/{user_id}/", response_model=dict, tags=["user_delete"])
async def delete_user(
    user_id: str,
    engine: Annotated[Engine, Depends(get_engine)],
) -> dict:
    logger.info(f"ユーザー削除リクエストを受け付けました。削除対象: {user_id}, ログイン中のユーザー: ")

    conditions = {"id": user_id}
    await delete_record(engine, UserDemo, conditions)
    logger.info(f"ユーザーを削除しました。ユーザーID: {user_id}")

    # 自分自身のアカウントを削除した場合はログアウト処理を行う
    # if current_user.id == user_id:
    #     response.delete_cookie("access_token")
    #     logger.info(
    #         f"ユーザー自身が削除されました。Cookieを削除し、ログアウト処理を実行します。"
    #     )
    #     return {"message": "User deleted and logged out successfully."}

    return {"message": "User deleted successfully"}
