from fastapi import APIRouter, Depends, HTTPException
from api.app.models import User  # SQLModelモデルをインポート
from api.app.dtos.user_dtos import (
    UserDTO,
    UserCreateDTO,
    UserSearchDTO,
    UserOrderBy,
    UserUpdateDTO
    )
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
from sqlmodel import select, Session

logger = getLogger(__name__)
router = APIRouter()


@router.post("/app/input/user/", response_model=UserDTO, tags=["user_post"])
@role_required(Role.ADMIN)
async def create_user(
    user: UserCreateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    # バリデーション用に Session を開く
    session = Session(engine)
    
    # 既存のメールアドレスのチェック
    existing_user = session.exec(
        select(User).where(User.email == user.email)).first()

    if existing_user:
        session.close()  # セッションを閉じる
        raise HTTPException(
            status_code=400, detail="Email already registered")
        
    # メールアドレスのバリデーション
    try:
        # EmailStrで形式のバリデーション
        valid_email = EmailStr(user.email)
    except ValueError:
        session.close()
        raise HTTPException(status_code=400, detail="Invalid email format")

    # セッションを閉じる
    session.close()

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user.password)

    # 新しいユーザーオブジェクトを作成
    user_data = User(
        name=user.name,
        email=user.email,
        password=hashed_password,  # ハッシュ化されたパスワードを保存
        authority=user.authority,
    )

    # データベースにレコードを追加
    await add_db_record(engine, user_data)

    # ログに情報を出力
    logger.info("新しいユーザーを登録します。")
    logger.info(f"ユーザーID:{user_data.id}")
    logger.info(f"ユーザー名:{user_data.name}")
    logger.info(f"E-mail:{user_data.email}")
    logger.info(f"権限情報:{user_data.authority}")

    # UserDTO を作成して返す
    user_dto = UserDTO(
        id=user_data.id,
        name=user_data.name,
        email=user_data.email,
        authority=user_data.authority
    )

    return user_dto



@router.get("/user/me", response_model=UserDTO, tags=["user_get"])
@role_required(Role.ADMIN)
async def get_me(current_user: User = Depends(get_current_user)):
    me_dto = UserDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        authority=current_user.authority
    )
    return me_dto


@router.get("/app/view/user/", response_model=list[UserDTO], tags=["user_get"])
@role_required(Role.ADMIN)  # admin権限が必要
async def view_user(
    search_params: UserSearchDTO = Depends(),
    order_by: Optional[UserOrderBy] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
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

    users = await select_table(
        engine,
        User,
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



@router.put("/app/update/user/{user_id}/", response_model=UserDTO, tags=["user_put"])
@role_required(Role.ADMIN)  # admin権限が必要
async def update_user(
    user_id: str,
    updates: UserUpdateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    updates_dict = updates.model_dump(exclude_unset=True)
    if "email" in updates_dict and updates_dict["email"]:
        try:
            # EmailStrのバリデーションを明示的に適用
            valid_email = EmailStr(updates_dict["email"])
        except ValueError:
            # EmailStrバリデーションで例外が発生した場合
            raise HTTPException(status_code=400, detail="Invalid email format")

    # パスワードのハッシュ化
    if 'password' in updates_dict:
        updates_dict['password'] = get_password_hash(updates_dict['password'])

    conditions = {"id": user_id}
    updated_record = await update_record(engine, User, conditions, updates)
    updated_user_dto = UserDTO(
        id=updated_record.id,
        name=updated_record.name,
        email=updated_record.email,
        authority=updated_record.authority
    )
    return updated_user_dto


@router.delete("/app/delete/user/{user_id}/", response_model=dict, tags=["user_delete"])
@role_required(Role.ADMIN)  # admin権限が必要
async def delete_user(
    user_id: str,
    engine=Depends(get_engine),
):
    conditions = {"id": user_id}
    result = await delete_record(engine, User, conditions)
    return result
