from sqlmodel import Session, create_engine, select
from dotenv import load_dotenv
import os
from os.path import join, dirname
from fastapi import HTTPException, Query
from typing import Optional
from api.logger import getLogger
from api.app.models import Users

logger = getLogger(__name__, "DEBUG")
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


def get_engine():
    engine = _get_engine()
    try:
        yield engine
    finally:
        engine.dispose()


def _get_engine():
    db_type = os.getenv("DB_TYPE")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    # 環境変数のデバッグ出力
    logger.debug(f"{db_type=}")
    logger.debug(f"{db_name=}")
    logger.debug(f"{db_user=}")
    logger.debug(f"{db_password=}")
    logger.debug(f"{db_host=}")
    logger.debug(f"{db_port=}")

    if db_type == "sqlite":
        database_url = f"{db_type}:///{db_name}"
    elif db_type == "postgresql":
        database_url = (
            f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
    elif db_type == "mysql":
        database_url = (
            f"{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
    else:
        raise ValueError(
            "Unsupported DB_TYPE. Use 'sqlite', 'postgresql', or 'mysql'.")
    engine = create_engine(database_url, echo=True)
    return engine


async def add_db_record(engine, data):
    with Session(engine) as session_db:
        try:
            session_db.add(data)
            session_db.commit()
            session_db.refresh(data)
            logger.debug(data)
        except Exception as e:
            session_db.rollback()
            raise HTTPException(
                status_code=470, detail=f"エラーが発生しました: {str(e)}"
            )


async def select_table(
    engine,
    table,
    limit: Optional[int] = Query(
        None, description="Limit the number of results returned"
    ),
    offset: Optional[int] = Query(0, description="Number of records to skip"),
):
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
            raise HTTPException(
                status_code=570, detail=f"エラーが発生しました: {str(e)}"
            )


async def update_record(
    engine,
    model,
    conditions: dict,
    updates: dict
):
    with Session(engine) as session_db:
        try:
            stmt = select(model)
            for field, value in conditions.items():
                stmt = stmt.where(getattr(model, field) == value)
            result = session_db.exec(stmt).one_or_none()
            if not result:
                raise HTTPException(status_code=404, detail="レコードが見つかりません")
            for field, value in updates.items():
                setattr(result, field, value)
            session_db.add(result)
            session_db.commit()
            session_db.refresh(result)
            return result
        except Exception as e:
            session_db.rollback()
            raise HTTPException(
                status_code=471, detail=f"エラーが発生しました: {str(e)}"
            )


async def delete_record(
    engine,
    model,
    conditions: dict
):
    with Session(engine) as session_db:
        try:
            stmt = select(model)
            for field, value in conditions.items():
                stmt = stmt.where(getattr(model, field) == value)
            result = session_db.exec(stmt).one_or_none()
            if not result:
                raise HTTPException(status_code=404, detail="レコードが見つかりません")
            # レコードの所有者チェック
            # if hasattr(result, 'user_id') and result.user_id != current_user.id:
            #     raise HTTPException(
            #         status_code=403, detail="このレコードを削除する権限がありません")
            session_db.delete(result)
            session_db.commit()
            return {"detail": "レコードが正常に削除されました"}
        except Exception as e:
            session_db.rollback()
            raise HTTPException(
                status_code=472, detail=f"エラーが発生しました: {str(e)}"
            )
