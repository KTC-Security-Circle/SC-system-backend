from fastapi import APIRouter
from datetime import datetime
from api.app.models import ChatLog  # SQLModelモデルをインポート
from api.app.database.database import get_engine,add_db_record

router = APIRouter()
engine = get_engine()

@router.post("/app/input/chat/", response_model=ChatLog)
async def create_chatlog(chatlog: ChatLog):
    chat_log_data = ChatLog(
        id=chatlog.id,
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=datetime.now(),
        session_id=chatlog.session_id
    )
    await add_db_record(engine,chat_log_data)  
    print(f"新しいチャットを登録します。\n\
チャットID:{chatlog.id}\nチャット内容:{chatlog.message}\nボットの返信:{chatlog.bot_reply}\n\
投稿日時:{chatlog.pub_data}\nセッションID:{chatlog.session_id}")
    
    return chat_log_data
