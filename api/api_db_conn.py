import sqlite3
from functools import wraps

def database(func):
    @wraps(func)
    async def database_conn(*args, **kwargs):
        dbname = 'test.db'  # データベース名を指定
        conn = sqlite3.connect(dbname)
        try:
            cur = conn.cursor()
            result = await func(cur, *args, **kwargs)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        return result
    return database_conn