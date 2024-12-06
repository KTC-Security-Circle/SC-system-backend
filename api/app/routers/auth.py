import logging
from collections.abc import Generator  # 型をインポート
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from api.app.database.engine import get_engine
from api.app.dtos.auth_dtos import LoginData
from api.app.dtos.user_dtos import UserCreateDTO, UserDTO
from api.app.models import User
from api.app.security.jwt_token import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from api.logger import getLogger

router = APIRouter()
logger = getLogger("auth_router", logging.DEBUG)


# セッション管理用の依存関数
def get_session() -> Generator[Session, None, None]:
    """
    データベースセッションを生成する依存関数。

    Yields:
        Session: SQLModelのデータベースセッション
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session

# サインアップエンドポイント
@router.post("/signup/", response_model=UserDTO, tags=["signup"])
async def signup(
    user: UserCreateDTO,  # リクエストボディとして受け取るユーザー情報
    session: Annotated[Session, Depends(get_session)],  # データベースセッションの依存関係
) -> UserDTO:
    """
    新しいユーザーを登録するエンドポイント。

    Args:
        user (UserCreateDTO): ユーザーの登録データ
        session (Session): データベースセッション

    Returns:
        UserDTO: 登録されたユーザーの情報
    """
    # ユーザーが既に登録済みかをチェック
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # パスワードをハッシュ化
    hashed_password = get_password_hash(user.password)

    # 新しいユーザーを作成
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        authority=user.authority,
        major=user.major,  # 専攻
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # DTO形式で返却
    return UserDTO(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        authority=new_user.authority,
        major=new_user.major,
    )


# ログインエンドポイント
@router.post("/login/", response_model=dict[str, str], tags=["login"])
async def login(
    user: LoginData,  # リクエストボディとしてログイン情報を受け取る
    response: Response,  # クッキー設定用のレスポンスオブジェクト
    session: Annotated[Session, Depends(get_session)],  # データベースセッションの依存関係
) -> dict[str, str]:
    """
    ユーザーを認証し、アクセストークンを発行するエンドポイント。

    Args:
        user (LoginData): ログイン情報
        response (Response): HTTPレスポンスオブジェクト
        session (Session): データベースセッション

    Returns:
        Dict[str, str]: トークンと追加情報
    """
    # ユーザーをデータベースから取得
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # アクセストークンの作成
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=timedelta(minutes=30),
    )

    # クッキーにトークンを設定
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
        secure=False,
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.authority,
        "message": "Login successful",
    }
