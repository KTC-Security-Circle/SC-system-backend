import pytest
from fastapi.testclient import TestClient
from app_fastapi import app 
from sqlmodel import SQLModel, Session
from api.app.models import Users  # SQLModelモデルをインポート
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
async def test_create_user(session):
    # テストデータの準備
    user_data = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "authority": "admin"
    }

    # POSTリクエストを送信
    response = client.post("/user/", json=user_data)
    
    # ステータスコードが200であることを確認
    assert response.status_code == 200
    
    # レスポンスデータの確認
    data = response.json()
    assert data["id"] == user_data["id"]
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["password"] == user_data["password"]
    assert data["authority"] == user_data["authority"]

    # データベースに保存されていることを確認
    with Session(engine) as session:
        user_in_db = session.get(Users, user_data["id"])
        assert user_in_db is not None
        assert user_in_db.name == user_data["name"]
        assert user_in_db.email == user_data["email"]
        assert user_in_db.password == user_data["password"]
        assert user_in_db.authority == user_data["authority"]
