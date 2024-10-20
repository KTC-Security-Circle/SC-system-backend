from api.app.dtos.user_dtos import (
    UserDTO,
    UserCreateDTO,
    UserSearchDTO,
    UserOrderBy,
    UserUpdateDTO
    )
from api.app.security.jwt_token import get_password_hash
from sqlmodel import select, Session

from api.app.routers import (
    logger,
    router,
    Depends,
    datetime,
    get_current_user,
    Role,
    role_required,
    Optional,
    add_db_record,
    get_engine,
    select_table,
    update_record,
    delete_record,
    User,
    HTTPException,
)


@router.post("/app/input/user/", response_model=UserDTO, tags=["user_post"])
@role_required(Role.ADMIN)
async def create_user(
    user: UserCreateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    
    logger.info("ユーザー作成リクエストを受け付けました。")

    session = Session(engine)
    
    # 既存のメールアドレスのチェック
    existing_user = session.exec(
        select(User).where(User.email == user.email)).first()

    if existing_user:
        session.close()
        logger.error(f"既に登録済みのメールアドレス: {user.email}")
        raise HTTPException(
            status_code=400, detail="Email already registered")

    session.close()

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user.password)

    # 新しいユーザーオブジェクトを作成
    user_data = User(
        name=user.name,
        email=user.email,
        password=hashed_password,  # ハッシュ化されたパスワードを保存
        authority=user.authority,
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
    logger.info(f"現在のユーザー情報を取得: {current_user.email}")
    me_dto = UserDTO(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        authority=current_user.authority
    )
    return me_dto


@router.get("/app/view/user/", response_model=list[UserDTO], tags=["user_get"])
@role_required(Role.ADMIN)
async def view_user(
    search_params: UserSearchDTO = Depends(),
    order_by: Optional[UserOrderBy] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
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

    users = await select_table(
        engine,
        User,
        conditions,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by
    )

    logger.info(f"ユーザー一覧取得完了: {len(users)}件")

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
@role_required(Role.ADMIN)
async def update_user(
    user_id: str,
    updates: UserUpdateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"ユーザー更新リクエストを受け付けました。ユーザーID: {user_id}")
    updates_dict = updates.model_dump(exclude_unset=True)
    
    session = Session(engine)

    # 既存のメールアドレスのチェック
    existing_user = session.exec(
        select(User).where(User.email == updates_dict['email'])).first()

    if existing_user:
        session.close()
        logger.info(f"ユーザー更新リクエストを受け付けました。ユーザーID: {user_id}")
        raise HTTPException(
            status_code=400, detail="Email already registered")

    session.close()

    if 'password' in updates_dict:
        updates_dict['password'] = get_password_hash(updates_dict['password'])

    conditions = {"id": user_id}
    updated_record = await update_record(engine, User, conditions, updates)
    logger.info(f"ユーザー情報を更新しました。ユーザーID: {updated_record.id}")
    updated_user_dto = UserDTO(
        id=updated_record.id,
        name=updated_record.name,
        email=updated_record.email,
        authority=updated_record.authority
    )
    return updated_user_dto


@router.delete("/app/delete/user/{user_id}/", response_model=dict, tags=["user_delete"])
@role_required(Role.ADMIN)
async def delete_user(
    user_id: str,
    engine=Depends(get_engine),
):
    logger.info(f"ユーザー削除リクエストを受け付けました。ユーザーID: {user_id}")

    conditions = {"id": user_id}
    result = await delete_record(engine, User, conditions)

    logger.info(f"ユーザーを削除しました。ユーザーID: {user_id}")

    return result
