from fastapi import HTTPException, status
from sqlmodel import Session, select
from api.app.models import Users
from api.app.database.database import get_engine
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
from os.path import join, dirname
import os

# .envファイルを読み込む
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 環境変数から設定を読み込む
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# 環境変数が存在しない場合のデフォルト値設定
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables")
if not ALGORITHM:
    raise ValueError("ALGORITHM is not set in the environment variables")
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
else:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_payload(user: Users) -> dict:
    """
    JWTペイロードを生成する関数。ユーザーIDとメールアドレスを含む。
    他の情報を追加したい場合はここに含める。
    """
    return {
        "sub": user.email,
        "user_id": user.id
    }


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    アクセストークンを作成する関数。
    デフォルトの有効期限は環境変数で設定されるが、明示的な期限を渡すこともできる。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_email(db: Session, email: str):
    statement = select(Users).where(Users.email == email)
    results = db.exec(statement)
    return results.first()


async def authenticate_user(db: Session, email: str, password: str):
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.password):
        return user
    return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with Session(get_engine()) as db:
        user = db.exec(select(Users).where(
            Users.id == user_id, Users.email == email)).first()
        if user is None:
            raise credentials_exception
        return user
