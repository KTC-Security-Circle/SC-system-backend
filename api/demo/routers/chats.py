from fastapi import APIRouter
from datetime import datetime
from api.app.models import ChatLog
from api.app.database.database import get_engine

router = APIRouter()

engine = get_engine()


@router.post("/chat/", response_model=ChatLog, tags=["chat"])
async def create_chatlog(chatlog: ChatLog):
    chat_log_data = ChatLog(
        id=chatlog.id,
        message=chatlog.message,
        bot_reply=chatlog.bot_reply,
        pub_data=datetime.now(),
        session_id=chatlog.session_id
    )
    return chat_log_data
