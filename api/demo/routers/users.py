from fastapi import APIRouter
from api.app.models import Users  # SQLModelモデルをインポート
from api.app.schemas.schemas import Users as Usersschemas
from api.app.database.database import get_engine  # 関数をインポート

router = APIRouter()

engine = get_engine()

@router.post("/user/", response_model=Users)
async def create_test_user(user: Usersschemas):
    user_data = Users(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        authority=user.authority,
    )
    return user_data