import logging
import os

from dotenv import load_dotenv
from sqlalchemy.engine.base import Engine
from sqlmodel import create_engine

# .envファイルから環境変数を読み込む
load_dotenv()

# ロガー設定
logger = logging.getLogger(__name__)

def get_engine() -> Engine:
    """
    データベースエンジンを生成する関数。

    Returns:
        Engine: SQLModelのデータベースエンジン
    """
    db_type: str | None = os.getenv("DB_TYPE")
    db_name: str | None = os.getenv("DB_NAME")
    db_user: str | None  = os.getenv("DB_USER")
    db_password: str | None  = os.getenv("DB_PASSWORD")
    db_host: str | None  = os.getenv("DB_HOST")
    db_port: str | None  = os.getenv("DB_PORT")

    # 環境変数のデバッグ出力
    logger.debug(f"DB_TYPE: {db_type}")
    logger.debug(f"DB_NAME: {db_name}")
    logger.debug(f"DB_USER: {db_user}")
    logger.debug(f"DB_PASSWORD: {'***' if db_password else None}")
    logger.debug(f"DB_HOST: {db_host}")
    logger.debug(f"DB_PORT: {db_port}")

    if db_type == "sqlite":
        database_url = f"sqlite:///{db_name}"
    elif db_type == "postgresql":
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == "mysql":
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == "sqlserver":
        database_url = f"mssql+pymssql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        raise ValueError("Unsupported DB_TYPE. Use 'sqlite', 'postgresql', 'mysql', or 'sqlserver'.")

    # データベースエンジンの作成
    engine = create_engine(
        database_url,
        echo=True,  # SQLクエリをログに出力
    )
    return engine
