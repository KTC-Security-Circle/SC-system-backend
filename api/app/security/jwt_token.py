from sqlmodel import Session, select
from api.app.models import User
from api.app.database.engine import get_engine
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import os
from api.logger import getLogger

logger = getLogger(__name__)

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

    try:
        # トークンをエンコード
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"アクセストークンの生成に成功しました: {encoded_jwt}")
        return encoded_jwt
    except JWTError as e:
        logger.error(f"トークンの生成中にエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="トークンの生成に失敗しました。再試行してください。",
        )
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="予期しないエラーが発生しました。",
        )


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_email(db: Session, email: str):
    statement = select(User).where(User.email == email)
    results = db.exec(statement)
    return results.first()


async def authenticate_user(db: Session, email: str, password: str):
    user = await get_user_by_email(db, email)
    if user and verify_password(password, user.password):
        return user
    return None


def get_current_user(
    token: str = Depends(oauth2_scheme), engine=Depends(get_engine)
) -> User:
    logger.debug(f"Received token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        logger.debug(f"Decoded token: email={email}, user_id={user_id}")
        if email is None or user_id is None:
            logger.error("Email or user_id is None")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decoding error: {str(e)}")
        raise credentials_exception

    try:
        with Session(engine) as db:
            user = db.exec(
                select(User).where(User.id == user_id, User.email == email)
            ).first()
            logger.debug(f"Retrieved user: {user}")
            if user is None:
                logger.error("User not found")
                raise credentials_exception
            return user
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise credentials_exception
