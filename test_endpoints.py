import requests
import json

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# 各エンドポイントに対するデータ
endpoints = [
    {
        "url": f"{base_url}/api/app/input/user/",
        "data": {"id": None, "name": "菅田将暉", "email": "exsample@num.jp", "password": "12345678", "authority": "admin"}
    },
    {
        "url": f"{base_url}/api/app/input/chat/",
        "data": {"id": None, "message": "テスト用テキスト", "bot_reply": "テスト用返信テキスト", "pub_data": None, "session_id": None}
    },
    {
        "url": f"{base_url}/api/app/input/session/",
        "data": {"id": None, "session_name": "Python", "pub_data": None, "user_id": None}
    },
    {
        "url": f"{base_url}/api/app/input/errorlog/",
        "data": {"id": None, "error_message": "テキストエラー", "pub_data": None, "session_id": None}
    }
]

# 各エンドポイントにPOSTリクエストを送信
for endpoint in endpoints:
    res = requests.post(endpoint["url"], json=endpoint["data"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")
