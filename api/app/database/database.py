# api/app/database/database.py
import logging
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select
from fastapi import HTTPException, status, Query
from functools import wraps
from typing import Optional

logger = logging.getLogger("database")

# デコレーターによるエラーハンドリング


def db_error_handling(default_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(
                    status_code=default_status_code,
                    detail=f"エラーが発生しました: {str(e)}"
                )
        return wrapper
    return decorator


@db_error_handling(default_status_code=470)
async def add_db_record(engine, data):
    with Session(engine) as session_db:
        session_db.add(data)
        session_db.commit()
        session_db.refresh(data)
        logger.debug(data)


@db_error_handling(default_status_code=570)
async def select_table(
    engine,
    model,
    conditions: Optional[dict] = None,
    like_conditions: Optional[dict] = None,  # LIKE条件を追加
    limit: Optional[int] = Query(
        None, description="Limit the number of results returned"),
    offset: Optional[int] = Query(0, description="Number of records to skip"),
    order_by: Optional[str] = None  # ORDER BY をサポート
):
    with Session(engine) as session:
        stmt = select(model)

        # 等価条件の追加
        if conditions:
            for field, value in conditions.items():
                stmt = stmt.where(getattr(model, field) == value)

        # LIKE条件の追加
        if like_conditions:
            for field, pattern in like_conditions.items():
                stmt = stmt.where(getattr(model, field).like(f"%{pattern}%"))

        # ORDER BY の追加
        if order_by:
            stmt = stmt.order_by(getattr(model, order_by))

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = session.exec(stmt)
        rows = result.all()
        return rows


@db_error_handling(default_status_code=471)
async def update_record(
    engine,
    model,
    conditions: dict,
    updates: dict
):
    try:
        with Session(engine) as session_db:
            # 条件に一致するレコードの検索
            stmt: Select = select(model)
            for field, value in conditions.items():
                stmt = stmt.where(getattr(model, field) == value)
            result = session_db.exec(stmt).one_or_none()

            # レコードが見つからない場合は404エラーを返す
            if not result:
                raise HTTPException(status_code=404, detail="レコードが見つかりません")

            # 更新対象のフィールドに新しい値を設定
            for field, value in updates.items():
                setattr(result, field, value)

            session_db.add(result)
            session_db.commit()
            session_db.refresh(result)
            return result

    except HTTPException as e:
        # すでに定義されているHTTPエラーを再度送出
        logger.error(f"HTTPエラーが発生しました: {e.detail}")
        raise

    except Exception as e:
        # その他の予期しないエラーをキャッチしてログに記録
        # ロールバックを行い、500エラーを返す
        session_db.rollback()
        logger.error(f"予期しないエラーが発生しました: {e}")
        raise HTTPException(
            status_code=500,
            detail="予期しないエラーが発生しました。"
        )


@db_error_handling(default_status_code=472)
async def delete_record(
    engine,
    model,
    conditions: dict
):
    with Session(engine) as session_db:
        stmt = select(model)
        for field, value in conditions.items():
            stmt = stmt.where(getattr(model, field) == value)
        result = session_db.exec(stmt).one_or_none()
        if not result:
            raise HTTPException(status_code=404, detail="レコードが見つかりません")
        session_db.delete(result)
        session_db.commit()
        return {"detail": "レコードが正常に削除されました"}
