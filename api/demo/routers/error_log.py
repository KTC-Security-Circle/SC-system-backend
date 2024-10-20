from fastapi import APIRouter
from datetime import datetime
from api.app.models import ErrorLog
from api.app.database.database import get_engine

router = APIRouter()

engine = get_engine()


@router.post("/errorlog/", response_model=ErrorLog, tags=["error_log"])
async def create_error_log(errorlog: ErrorLog):
    error_log_data = ErrorLog(
        id=errorlog.id,
        error_message=errorlog.error_message,
        pub_data=datetime.now(),
        session_id=errorlog.session_id
    )
    return error_log_data
