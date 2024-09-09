from fastapi import APIRouter
from datetime import datetime
from api.app.models import Session
from api.app.database.database import get_engine

router = APIRouter()

engine = get_engine()


@router.post("/session/", response_model=Session, tags=["session"])
async def create_session(session: Session):
    session_data = Session(
        id=session.id,
        session_name=session.session_name,
        pub_data=datetime.now(),
        user_id=session.user_id,
    )
    return session_data
