import logging
from collections.abc import Generator
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
@router.post("/signup", response_model=UserDTO, tags=["signup"])
async def signup(user: UserCreateDTO, session: Annotated[Session, Depends(get_session)]) -> UserDTO:
    logger.debug("Signup API called with user data: %s", user.dict())
    try:
        # ユーザーの存在確認
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        logger.debug("Existing user query result: %s", existing_user)

        if existing_user:
            logger.warning("Attempted to register with existing email: %s", user.email)
            raise HTTPException(status_code=400, detail="Email already registered")

        # パスワードをハッシュ化して保存
        hashed_password = get_password_hash(user.password)
        logger.debug("Hashed password: %s", hashed_password)

        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            authority=user.authority,
            major=user.major,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        logger.info("New user created: %s", new_user.dict())

        # ユーザー情報をDTO形式で返す
        signup_dto = UserDTO(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            authority=new_user.authority,
            major=new_user.major,
        )
        logger.debug("Signup DTO: %s", signup_dto.dict())
        return signup_dto
    except Exception as e:
        logger.error("Error in signup endpoint: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during signup")


# ログインエンドポイント
@router.post("/login", response_model=dict, tags=["login"])
async def login(user: LoginData, response: Response, session: Annotated[Session, Depends(get_session)]) -> dict:
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # トークンにメールアドレスとユーザーIDを含める
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=timedelta(minutes=30),
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
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
