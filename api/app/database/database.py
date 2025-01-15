# api/app/database/database.py
import logging
from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, select

logger = logging.getLogger("database")

# デコレーターによるエラーハンドリング


T = TypeVar("T")
M = TypeVar("M", bound=SQLModel)


def db_error_handling(
    default_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                logger.debug(
                    "DB function called: %s, args: %s, kwargs: %s",
                    func.__name__,
                    args,
                    kwargs,
                )
                return func(*args, **kwargs)
            except HTTPException as e:
                logger.error("HTTP exception in DB function: %s", str(e), exc_info=True)
                raise
            except Exception as e:
                logger.error(
                    "Unhandled exception in DB function: %s", str(e), exc_info=True
                )
                raise HTTPException(
                    status_code=default_status_code,
                    detail=f"Database error occurred: {str(e)}",
                ) from e

        return wrapper

    return decorator


@db_error_handling(default_status_code=470)
async def add_db_record(engine: Engine, data: SQLModel) -> None:
    with Session(engine) as session_db:
        session_db.add(data)
        session_db.commit()
        session_db.refresh(data)
        logger.debug(data)


@db_error_handling(default_status_code=570)
async def select_table(
    engine: Engine,
    model: type[M],
    conditions: dict | None = None,
    like_conditions: dict | None = None,  # LIKE条件を追加
    limit: int | None = None,  # Queryを外して直接Optional[int]
    offset: int | None = 0,
    order_by: str | None = None,  # ORDER BY をサポート
) -> Sequence[M]:
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
async def update_record(engine: Engine, model: type[M], conditions: dict, updates: dict) -> M:
    try:
        with Session(engine) as session_db:
            # 条件に一致するレコードの検索
            stmt = select(model)
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
        raise HTTPException(status_code=500, detail="予期しないエラーが発生しました。") from e


@db_error_handling(default_status_code=472)
async def delete_record(engine: Engine, model: type[M], conditions: dict) -> dict[str, str]:
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
