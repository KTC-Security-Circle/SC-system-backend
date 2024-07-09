import requests
import json

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# 各エンドポイントに対するデータ
post_endpoints = [
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
get_endpoints = [
  {
    "url": f"{base_url}/api/app/view/user/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/view/chat/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/view/session/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/view/errorlog/",# ?limit=2&offset=1
  }
]
put_endpoints = [
  {
    "url": f"{base_url}/api/app/update/user/1/",
    "data": {"name": "更新済み", "email": "更新済み", "password": "77777777", "authority": "update"}
  },
  {
    "url": f"{base_url}/api/app/update/chat/1/",
    "data": {"message": "更新済みテキスト", "bot_reply": "更新済み返信テキスト"}
  },
  {
    "url": f"{base_url}/api/app/update/session/1/",
    "data": {"session_name": "更新済み"}
  },
  {
    "url": f"{base_url}/api/app/update/errorlog/1/",
    "data": {"error_message": "更新済み"}
  }
]


# 各エンドポイントにPOSTリクエストを送信
for endpoint in post_endpoints:
  try:
    res = requests.post(endpoint["url"], json=endpoint["data"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")
  except requests.exceptions.RequestException as e:
    print(f"Request to {endpoint['url']} failed: {e}")
for endpoint in get_endpoints:
  try:
    res = requests.get(endpoint["url"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")
  except requests.exceptions.RequestException as e:
    print(f"Request to {endpoint['url']} failed: {e}")
for endpoint in put_endpoints:
  try:
    res = requests.put(endpoint["url"], json=endpoint["data"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")
  except requests.exceptions.RequestException as e:
    print(f"Request to {endpoint['url']} failed: {e}")