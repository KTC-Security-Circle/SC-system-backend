from fastapi import APIRouter
from datetime import datetime
from api.app.models import ErrorLog  # SQLModelモデルをインポート
from api.app.database.database import get_engine,add_db_record

router = APIRouter()

engine = get_engine()

@router.post("/app/input/errorlog/", response_model=ErrorLog)
async def create_error_log(errorlog: ErrorLog):
    error_log_data = ErrorLog(
        id=errorlog.id,
        error_message=errorlog.error_message,
        pub_data=datetime.now(),
        session_id=errorlog.session_id
    )
    await add_db_record(engine,error_log_data)
    print(f"エラーが発生しました。\n\
エラーID:{errorlog.id}\nエラー名:{errorlog.error_message}\n投稿日時:{errorlog.pub_data}\nセッションID:{errorlog.session_id}")
    
    return error_log_data
