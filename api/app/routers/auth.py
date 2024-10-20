from sqlmodel import Session, select
from api.app.security.jwt_token import create_access_token, get_password_hash, verify_password
from api.app.dtos.auth_dtos import Token, LoginData
from api.app.dtos.user_dtos import UserDTO, UserCreateDTO
from datetime import timedelta

from api.app.routers import (
    router,
    Depends,
    get_engine,
    User,
    HTTPException,
    Response,
)


@router.post("/signup/", response_model=UserDTO, tags=["signup"])
async def signup(user: UserCreateDTO, engine=Depends(get_engine)):
    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered")
        hashed_password = get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,  # パスワードをハッシュ化して保存
            authority=user.authority  # 必要に応じてユーザー権限も保存
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        signup_dto = UserDTO(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            authority=new_user.authority
        )
        return signup_dto


@router.post("/login/", response_model=dict, tags=["login"])
async def login(user: LoginData, response: Response, engine=Depends(get_engine)):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(
            User.email == user.email)).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=400, detail="Invalid email or password")

        # トークンにメールアドレスとユーザーIDを含める
        access_token = create_access_token(
            data={"sub": db_user.email, "user_id": db_user.id},
            expires_delta=timedelta(minutes=30)
            )
        
        response.set_cookie(
            key="access_token",           # Cookie名
            value=access_token,           # Cookieの値にトークンを設定
            httponly=False,                # HttpOnlyに設定して、JSからのアクセスを禁止(javascriptで触りたいのでFalse)
            max_age=1800,                 # 30分の有効期限
            expires=1800,                 # 同じく30分でCookieを無効化
            secure=False,                  # HTTPSのみで送信(開発中はFalse)
            samesite="Lax"                # CSRF対策
        )
        return {"message": "Login successful"}