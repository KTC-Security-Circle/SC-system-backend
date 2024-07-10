import requests
import json

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# 各エンドポイントに対するデータ
endpoints = [
    {
        "url": f"{base_url}/demo/user/",
        "data": {"id": 2, "name": "菅田将暉", "email": "exsample@num.jp", "password": "12345678", "authority": "admin"}
    },
    {
        "url": f"{base_url}/demo/chat/",
        "data": {"id": 3, "message": "テスト用テキスト", "bot_reply": "テスト用返信テキスト", "pub_data": None, "session_id": 2}
    },
    {
        "url": f"{base_url}/demo/session/",
        "data": {"id": 3, "session_name": "Python", "pub_data": None, "user_id": 2}
    },
    {
        "url": f"{base_url}/demo/errorlog/",
        "data": {"id": 3, "error_message": "テキストエラー", "pub_data": None, "session_id": 2}
    }
]

# 各エンドポイントにPOSTリクエストを送信
for endpoint in endpoints:
    res = requests.post(endpoint["url"], json=endpoint["data"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")