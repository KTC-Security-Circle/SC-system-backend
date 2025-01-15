from datetime import timedelta

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
logger = getLogger("auth_router")

# サインアップエンドポイント


@router.post("/signup/", response_model=UserDTO, tags=["signup"])
async def signup(user: UserCreateDTO, engine=Depends(get_engine)):
    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # パスワードをハッシュ化して保存
        hashed_password = get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            authority=user.authority,
            major=user.major,  # 専攻を追加
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # ユーザー情報をDTO形式で返す
        signup_dto = UserDTO(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            authority=new_user.authority,
            major=new_user.major,  # 専攻を追加
        )
        return signup_dto


# ログインエンドポイント
@router.post("/login/", response_model=dict, tags=["login"])
async def login(user: LoginData, response: Response, engine=Depends(get_engine)):
    with Session(engine) as session:
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
            samesite="Lax",
        )
        return {
            "access_token": access_token,
             "role":db_user.authority,
            "token_type": "bearer",
            "message": "Login successful",
        }
