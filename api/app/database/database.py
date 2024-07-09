from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os
from fastapi import HTTPException

load_dotenv()  # .envファイルから環境変数を読み込み

def get_engine():
    db_type = os.getenv("DB_TYPE", "sqlite")
    db_name = os.getenv("DB_NAME", "database.db")
    db_user = os.getenv("DB_USER", "")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "")

    if db_type == "sqlite":
        database_url = f"{db_type}:///{db_name}"
    elif db_type == "postgresql":
        database_url = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == "mysql":
        database_url = f"{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        raise ValueError("Unsupported DB_TYPE. Use 'sqlite', 'postgresql', or 'mysql'.")
    engine  = create_engine(database_url, echo=True)
    return engine

async def add_db_record(engine,data):
  with Session(engine) as session_db:
          try:
              session_db.add(data)
              session_db.commit()
              session_db.refresh(data)
              print(data)
          except Exception as e:
              session_db.rollback()
              raise HTTPException(status_code=400, detail=f"エラーが発生しました: {str(e)}")