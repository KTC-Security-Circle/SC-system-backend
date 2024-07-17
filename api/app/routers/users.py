from fastapi import APIRouter
from api.app.models import Users
from api.app.database.database import engine,add_db_record,select_table,update_record,delete_record
from typing import Optional
import json

router = APIRouter()

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

@router.get("/app/view/user/", response_model=list[Users])
async def view_users(conditions: Optional[str]  = None,limit: Optional[int] = None, offset: Optional[int] = 0):
  if conditions != None:
    conditions = json.loads(conditions)
  users = await select_table(engine,Users,conditions=conditions, limit=limit, offset=offset)
  print(users)
  return users

@router.put("/app/update/user/{user_id}/", response_model=Users)
async def update_users(user_id: int, updates: dict[str, str]):
  conditions = {"id": user_id}
  updated_record = await update_record(engine, Users, conditions, updates)
  return updated_record

@router.delete("/app/delete/user/{user_id}/", response_model=dict)
async def delete_user(user_id: int):
  conditions = {"id": user_id}
  result = await delete_record(engine, Users, conditions)
  return result