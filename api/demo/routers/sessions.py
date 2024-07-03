from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from datetime import datetime
from api.demo.models.database_sqlmodel import Sessions  # SQLModelモデルをインポート
from create_database_sqmodel import get_engine

router = APIRouter()

engine = get_engine()

@router.post("/session/", response_model=Sessions)
async def create_sessions(session: Sessions):
    session_data = Sessions(
        id=session.id,
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=session.user_id,
    )
    with Session(engine) as session_db:
        try:
            session_db.add(session_data)
            session_db.commit()
            session_db.refresh(session_data)
        except Exception as e:
            session_db.rollback()
            raise HTTPException(status_code=400, detail=f"エラーが発生しました: {str(e)}")
    print(f"新しいセッションを登録します。\n\
セッションID:{session.id}\nセッション名:{session.session_name}\n投稿日時:{session.pub_data}\nユーザーID:{session.user_id}")

    return session_data