from fastapi import APIRouter, HTTPException
from ..models.database import Users
from ..schemas.message import Message
from ...api_db_conn import database
import sqlite3

router = APIRouter()

@database
async def insert_user(cur, user: Users):
    try:
        cur.execute("""
            INSERT INTO users (id, name, email, password, authority)
            VALUES (?, ?, ?, ?, ?)
        """, (user.id, user.name, user.email, user.password, user.authority))
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail="ユーザーIDが既に存在します")

@router.post("/users/", response_model=Message)
async def create_user(user: Users):
    await insert_user(user)
    print(f"新しいユーザーを登録します。\n\
ユーザーID:{user.id}\nユーザー名:{user.name}\nE-mail:{user.email}\nパスワード:{user.password}\n権限情報:{user.authority}")
    result = Message(content=f"{user.name}の登録が完了しました。")
    return result