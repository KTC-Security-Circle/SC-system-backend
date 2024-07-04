from fastapi import APIRouter
from datetime import datetime
from api.app.models import ChatLog  # SQLModelモデルをインポート
from api.app.schemas.schemas import ChatLog as ChatLogschemas
from api.app.database.database import get_engine  # 関数をインポート

router = APIRouter()

engine = get_engine()

@router.post("/chat/", response_model=ChatLog)
async def create_chatlog(chatlog: ChatLogschemas):
    chat_log_data = ChatLog(
        id=chatlog.id,
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=datetime.now(),
        session_id=chatlog.session_id
    )
    return chat_log_data
