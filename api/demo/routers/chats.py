from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from datetime import datetime
from api.demo.models.database_sqlmodel import ChatLog  # SQLModelモデルをインポート
from create_database_sqmodel import get_engine  # 関数をインポート

router = APIRouter()

engine = get_engine()

@router.post("/chat/", response_model=ChatLog)
async def create_chatlog(chatlog: ChatLog):
    chat_log_data = ChatLog(
        id=chatlog.id,
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=datetime.now(),
        session_id=chatlog.session_id
    )
    with Session(engine) as session_db:
        try:
            session_db.add(chat_log_data)
            session_db.commit()
            session_db.refresh(chat_log_data)
        except Exception as e:
            session_db.rollback()
            raise HTTPException(status_code=400, detail=f"エラーが発生しました: {str(e)}")
    
    print(f"新しいチャットを登録します。\n\
チャットID:{chatlog.id}\nチャット内容:{chatlog.message}\nボットの返信:{chatlog.bot_reply}\n\
投稿日時:{chatlog.pub_data}\nセッションID:{chatlog.session_id}")
    
    return chat_log_data
