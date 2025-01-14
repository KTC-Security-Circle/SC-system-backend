import logging
import os

from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlmodel import create_engine

# .envファイルから環境変数を読み込む
load_dotenv()

# ロガー設定
logger = logging.getLogger(__name__)


def get_engine() -> Engine:
    try:
        db_type = os.getenv("DB_TYPE")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")

        # 環境変数のデバッグ出力
        logger.debug(f"DB_TYPE: {db_type}")
        logger.debug(f"DB_NAME: {db_name}")
        logger.debug(f"DB_USER: {db_user}")
        logger.debug(f"DB_PASSWORD: {db_password}")
        logger.debug(f"DB_HOST: {db_host}")
        logger.debug(f"DB_PORT: {db_port}")

        if db_type == "sqlite":
            database_url = f"{db_type}:///{db_name}"
        elif db_type == "postgresql":
            database_url = (
                f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
        elif db_type == "mysql":
            database_url = f"{db_type}+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif db_type == "sqlserver":
            database_url = (
                f"mssql+pymssql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )
        else:
            raise ValueError(
                "Unsupported DB_TYPE. Use 'sqlite', 'postgresql', or 'mysql'."
            )

        logger.debug(f"Database URL: {database_url}")
        engine = create_engine(database_url, echo=True)
        return engine
    except Exception as e:
        logger.error("Error creating database engine: %s", str(e), exc_info=True)
        raise
