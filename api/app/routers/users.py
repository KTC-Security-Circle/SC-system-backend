from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from api.app.models import Users  # SQLModelモデルをインポート
from api.app.schemas.schemas import Users as Usersschemas
from api.app.database.database import get_engine  # 関数をインポート

router = APIRouter()

engine = get_engine()

@router.post("/app/user/", response_model=Users)
async def create_users(user: Usersschemas):
    user_data = Users(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        authority=user.authority,
    )
    with Session(engine) as session_db:
        try:
            session_db.add(user_data)
            session_db.commit()
            session_db.refresh(user_data)
        except Exception as e:
            session_db.rollback()
            raise HTTPException(status_code=400, detail=f"エラーが発生しました: {str(e)}")
    print(f"新しいユーザーを登録します。\n\
ユーザーID:{user.id}\nユーザー名:{user.name}\nE-mail:{user.email}\nパスワード:{user.password}\n権限情報:{user.authority}")
    
    return user_data
