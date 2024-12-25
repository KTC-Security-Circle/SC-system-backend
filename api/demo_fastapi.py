import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

# サードパーティライブラリ
from fastapi import FastAPI
from sqlmodel import SQLModel

# ローカルモジュール
from api.app.database.engine import get_engine
from api.demo.routers.chats import router as chatlog_demo_router
from api.demo.routers.sessions import router as session_demo_router
from api.demo.routers.users import router as user_demo_router
from api.logger import getLogger

# ロガーの設定
# ログを出力するカスタムロガーを取得し、デバッグレベルに設定
logger = getLogger("azure_functions.fastapi", logging.DEBUG)


# FastAPI アプリケーションのライフスパン管理
# アプリの起動時と終了時にリソースの初期化と解放を行う
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # データベースエンジンを取得
        engine = get_engine()

        # 既存のテーブルを削除して再作成する処理 (必要に応じてコメント解除)
        # SQLModel.metadata.drop_all(engine)

        # テーブルの作成（既存テーブルがない場合のみ実行）
        SQLModel.metadata.create_all(engine)
        logger.info("Database connected and tables created.")

        # アプリケーションのライフスパン中にリソースを使用可能
        yield
    except Exception as e:
        # データベースの初期化中にエラーが発生した場合
        logger.error("Error during database setup: %s", e)
        raise
    finally:
        # アプリケーション終了時にデータベース接続を解放
        engine.dispose()
        logger.info("Database connection closed.")


# FastAPI アプリケーションインスタンスの作成
# lifespan 関数で定義したリソース管理を登録
app = FastAPI(lifespan=lifespan)

# CORS 設定のオリジン（許可されるリクエスト元のリスト）
# 動的設定は不要なため、静的に設定
origins: list[str] = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:7071",
    "https://sc-test-api.azurewebsites.net",
]

# ルーターの登録
# 各モジュールのエンドポイントを FastAPI アプリに追加
routers = [
    (user_demo_router, "/api"),  # ユーザー関連のエンドポイント
    (session_demo_router, "/api"),  # セッション関連のエンドポイント
    (chatlog_demo_router, "/api"),  # チャットログ関連のエンドポイント
]

# ルーターをアプリケーションに登録
for router, prefix in routers:
    app.include_router(router, prefix=prefix)
