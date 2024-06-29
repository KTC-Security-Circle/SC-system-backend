from fastapi import APIRouter
from ..schemas.token import Token
from ..models.user import fake_users_db

router = APIRouter()

@router.post("/token", response_model=Token)
async def login():
    return {"access_token": "dummy_token", "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me():
    return {
        "username": "demo_user",
        "email": "demo_user@example.com",
        "full_name": "Demo User",
        "disabled": False,
    }
