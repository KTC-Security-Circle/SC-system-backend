from sqlmodel import Session, create_engine,select
from dotenv import load_dotenv
import os
from os.path import join, dirname
from fastapi import HTTPException,Query
from typing import Optional

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def get_engine():
    db_type = os.getenv("DB_TYPE")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    
    # 環境変数のデバッグ出力
    print(f"DB_TYPE: {db_type}")
    print(f"DB_NAME: {db_name}")
    print(f"DB_USER: {db_user}")
    print(f"DB_PASSWORD: {db_password}")
    print(f"DB_HOST: {db_host}")
    print(f"DB_PORT: {db_port}")
    
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
engine = get_engine()


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

def select_table(engine, table, limit: Optional[int] = Query(None, description="Limit the number of results returned"),
offset: Optional[int] = Query(0, description="Number of records to skip")):
    with Session(engine) as session:
        try:
            stmt = select(table)
            if offset:
                stmt = stmt.offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            result = session.exec(stmt)
            rows = result.all()
            return rows
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")
