import pytest
from fastapi.testclient import TestClient
from app_fastapi import app 
from sqlmodel import SQLModel, Session
from api.app.models import Sessions  # SQLModelモデルをインポート
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
async def test_create_session(session):
    # テストデータの準備
    session_data = {
        "id": 1,
        "session_name": "Test Session",
        "pub_data": None,
        "user_id": 1
    }

    # POSTリクエストを送信
    response = client.post("/session/", json=session_data)
    
    # ステータスコードが200であることを確認
    assert response.status_code == 200
    
    # レスポンスデータの確認
    data = response.json()
    assert data["id"] == session_data["id"]
    assert data["session_name"] == session_data["session_name"]
    assert data["user_id"] == session_data["user_id"]

    # データベースに保存されていることを確認
    with Session(engine) as session:
        session_in_db = session.get(Sessions, session_data["id"])
        assert session_in_db is not None
        assert session_in_db.session_name == session_data["session_name"]
        assert session_in_db.user_id == session_data["user_id"]