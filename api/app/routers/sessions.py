from fastapi import APIRouter
from datetime import datetime
from api.app.models import Sessions  # SQLModelモデルをインポート
from api.app.database.database import get_engine,add_db_record

router = APIRouter()

engine = get_engine()

@router.post("/app/input/session/", response_model=Sessions)
async def create_sessions(session: Sessions):
    session_data = Sessions(
        id=session.id,
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=session.user_id,
    )
    await add_db_record(engine,session_data)
    print(f"新しいセッションを登録します。\n\
セッションID:{session.id}\nセッション名:{session.session_name}\n投稿日時:{session.pub_data}\nユーザーID:{session.user_id}")

    return session_data