from fastapi import APIRouter
from datetime import datetime
from api.app.models import Sessions  # SQLModelモデルをインポート
from api.app.schemas.schemas import Sessions as Sessionsschemas
from api.app.database.database import get_engine

router = APIRouter()

engine = get_engine()

@router.post("/session/", response_model=Sessions)
async def create_sessions(session: Sessionsschemas):
    session_data = Sessions(
        id=session.id,
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=session.user_id,
    )
    return session_data