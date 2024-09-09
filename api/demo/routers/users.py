from fastapi import APIRouter
from api.app.models import User
from api.app.database.database import get_engine

router = APIRouter()

engine = get_engine()


@router.post("/user/", response_model=User, tags=["user"])
async def create_test_user(user: User):
    user_data = User(
        id=user.id,
        name=user.name,
        email=user.email,
        password=user.password,
        authority=user.authority,
    )
    return user_data
