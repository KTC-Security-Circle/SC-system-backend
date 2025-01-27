import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from api.app.database.engine import get_engine
from api.app.routers.auth import router as auth_router
from api.app.routers.chats import router as chatlog_router
from api.app.routers.group import router as group_router
from api.app.routers.school_info import router as school_info_router
from api.app.routers.sessions import router as session_router
from api.app.routers.users import router as user_router
from api.logger import getLogger

logger = getLogger("azure_functions.fastapi")
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # データベースエンジンの作成
        engine = get_engine()

        # 既存のテーブルを削除して再作成する処理 (必要に応じてコメント解除)
        # SQLModel.metadata.drop_all(engine)

        # データベーステーブルの作成
        SQLModel.metadata.create_all(engine)
        logger.info("Database connected and tables created.")

        # アプリケーションのライフスパン中にリソースを使用可能
        yield
    except Exception as e:
        # データベース設定中のエラーをロギング
        logger.error("Error during database setup: %s", e)
        raise
    finally:
        # アプリケーション終了時にエンジンを解放
        engine.dispose()
        logger.info("Database connection closed.")


# FastAPI アプリケーションの作成
# lifespan を登録してアプリケーションのリソースを管理
app = FastAPI(lifespan=lifespan)

@app.get("/test-streaming")
async def test_streaming():
    """
    StreamingResponseが動作するかをテストする関数
    """

    async def generator():
        for i in range(10):  # 10個のメッセージを送信
            yield f"data: Message {i}\n\n"
            await asyncio.sleep(1)  # 1秒間隔でメッセージを送信

    # StreamingResponseを返す
    return StreamingResponse(generator(), media_type="text/event-stream")

# CORS 設定
# 特定のオリジンからのリクエストを許可する
origins: list[str] = [
    "http://localhost",  # ローカルホストでの開発用
    "http://localhost:3000",  # フロントエンド (React.js など)
    "http://localhost:7071",  # Azure Functions のローカル実行
    "https://sc-test-api.azurewebsites.net",  # 本番環境
]

# CORS ミドルウェアの追加
# リクエスト元やメソッド、ヘッダーの制限を設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 許可する HTTP メソッド
    allow_headers=["Content-Type", "Authorization"],  # 許可するヘッダー
)

# ルーターの登録
# 各モジュールのエンドポイントを FastAPI アプリに追加
routers = [
    (auth_router, "/auth"),  # 認証関連のエンドポイント
    (user_router, "/api"),  # ユーザー関連のエンドポイント
    (session_router, "/api"),  # セッション関連のエンドポイント
    (chatlog_router, "/api"),  # チャットログ関連のエンドポイント
    (group_router, "/api"),  # グループ関連のエンドポイント
    (school_info_router, "/api"),  # 学校情報関連のエンドポイント
]

# ルーターをアプリケーションに登録
for router, prefix in routers:
    app.include_router(router, prefix=prefix)
