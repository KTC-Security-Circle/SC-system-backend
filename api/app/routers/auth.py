from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from api.app.models import Users
from api.app.database.database import get_engine
from api.app.security.jwt_token import create_access_token, get_password_hash, verify_password
from api.app.schemas.token import Token,LoginData

router = APIRouter()

engine = get_engine()

@router.post("/signup/", response_model=Users)
async def signup(user: Users):
  with Session(engine) as session:
    existing_user = session.exec(select(Users).where(Users.email == user.email)).first()
    if existing_user:
      raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login/", response_model=Token)
async def login(user: LoginData):
  with Session(engine) as session:
    db_user = session.exec(select(Users).where(Users.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}