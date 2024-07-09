from fastapi import APIRouter
from api.app.models import Users  # SQLModelモデルをインポート
from api.app.database.database import get_engine,add_db_record

router = APIRouter()

engine = get_engine()

@router.post("/app/input/user/", response_model=Users)
async def create_users(user: Users):
    user_data = Users(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        authority=user.authority,
    )
    await add_db_record(engine,user_data)
    print(f"新しいユーザーを登録します。\n\
ユーザーID:{user.id}\nユーザー名:{user.name}\nE-mail:{user.email}\nパスワード:{user.password}\n権限情報:{user.authority}")
    
    return user_data
