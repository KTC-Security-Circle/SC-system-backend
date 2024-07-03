from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from datetime import datetime
from api.demo.models.database_sqlmodel import ErrorLog  # SQLModelモデルをインポート
from api.demo.schemas.database import ErrorLog as ErrorLogschemas
from create_database_sqmodel import get_engine

router = APIRouter()

engine = get_engine()

@router.post("/errorlog/", response_model=ErrorLog)
async def create_error_log(errorlog: ErrorLogschemas):
    error_log_data = ErrorLog(
        id=errorlog.id,
        error_message=errorlog.error_message,
        pub_data=datetime.now(),
        session_id=errorlog.session_id
    )
    with Session(engine) as session:
        try:
            session.add(error_log_data)
            session.commit()
            session.refresh(error_log_data)
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail=f"エラーが発生しました: {str(e)}")
    print(f"エラーが発生しました。\n\
エラーID:{errorlog.id}\nエラー名:{errorlog.error_message}\n投稿日時:{errorlog.pub_data}\nセッションID:{errorlog.session_id}")
    
    return error_log_data
