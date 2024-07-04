import pytest
from fastapi.testclient import TestClient
from app_fastapi import app 
from sqlmodel import SQLModel, Session
from api.app.models import ErrorLog  # SQLModelモデルをインポート
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
async def test_create_errorlog(session):
    # テストデータの準備
    errorlog_data = {
        "id": 1,
        "error_message": "Test error",
        "pub_data": None,
        "session_id": 1
    }

    # POSTリクエストを送信
    res = client.post("/errorlog/", json=errorlog_data)
    
    # ステータスコードが200であることを確認
    assert res.status_code == 200
    
    # レスポンスデータの確認
    data = res.json()
    assert data["id"] == errorlog_data["id"]
    assert data["error_message"] == errorlog_data["error_message"]
    assert data["session_id"] == errorlog_data["session_id"]

    # データベースに保存されていることを確認
    with Session(engine) as session:
        errorlog_in_db = session.get(ErrorLog, errorlog_data["id"])
        assert errorlog_in_db is not None
        assert errorlog_in_db.error_message == errorlog_data["error_message"]
        assert errorlog_in_db.session_id == errorlog_data["session_id"]
