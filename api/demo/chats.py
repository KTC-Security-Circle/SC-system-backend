import pytest
from fastapi.testclient import TestClient
from app_fastapi import app
from sqlmodel import SQLModel, Session
from api.app.models import ChatLog  # SQLModelモデルをインポート
from api.app.database.database import get_engine  # 関数をインポート

client = TestClient(app)
engine = get_engine()

# テスト用のデータベースの設定
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_create_chatlog(session):
    # テストデータの準備
    chatlog_data = {
        "id": 1,
        "message": "Hello, world!",
        "bot_reply": "Hello!",
        "pub_data": None,
        "session_id": 1
    }

    # POSTリクエストを送信
    response = client.post("/chat/", json=chatlog_data)
    
    # ステータスコードが200であることを確認
    assert response.status_code == 200
    
    # レスポンスデータの確認
    data = response.json()
    assert data["id"] == chatlog_data["id"]
    assert data["message"] == chatlog_data["message"]
    assert data["bot_reply"] == chatlog_data["bot_reply"]
    assert data["session_id"] == chatlog_data["session_id"]

    # データベースに保存されていることを確認
    with Session(engine) as session:
        chatlog_in_db = session.get(ChatLog, chatlog_data["id"])
        assert chatlog_in_db is not None
        assert chatlog_in_db.message == chatlog_data["message"]
        assert chatlog_in_db.bot_reply == chatlog_data["bot_reply"]
        assert chatlog_in_db.session_id == chatlog_data["session_id"]
