import requests
import json

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# 各エンドポイントに対するデータ
post_endpoints = [
  {
    "url": f"{base_url}/api/app/input/user/",
    "data": {"id": None, "name": "aaaaaa", "email": "exsample@num.jp", "password": "12345678", "authority": "admin"}
  },
  {
    "url": f"{base_url}/api/app/input/chat/",
    "data": {"id": None, "message": "aaaaaa", "bot_reply": "テスト用返信テキスト", "pub_data": None, "session_id": 1}
  },
  {
    "url": f"{base_url}/api/app/input/session/",
    "data": {"id": None, "session_name": "Python", "pub_data": None, "user_id": 1}
  },
  {
    "url": f"{base_url}/api/app/input/errorlog/",
    "data": {"id": None, "error_message": "テキストエラー", "pub_data": None, "session_id": 1}
  }
]
get_endpoints = [
    {
        "url": f"{base_url}/api/app/view/user/",
        "params": {
            "limit": 2,
            "offset": 1,
            "conditions": json.dumps({"name": "aaaaaa"})
        }
    },
    {
        "url": f"{base_url}/api/app/view/chat/",
        "params": {
            "limit": 3,
            "offset": 1,
            "conditions": json.dumps({"session_id": 1})
        }
    },
    {
        "url": f"{base_url}/api/app/view/session/",
        "params": {
            "limit": 3,
            "offset": 1,
            "conditions": json.dumps({"user_id": 1})
        }
    },
    {
        "url": f"{base_url}/api/app/view/errorlog/",
        "params": {
            "limit": 3,
            "offset": 1,
            "conditions": json.dumps({"session_id": 1})
        }
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
delete_endpoints = [
  {
    "url": f"{base_url}/api/app/delete/user/1/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/delete/chat/1/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/delete/session/1/",# ?limit=2&offset=1
  },
  {
    "url": f"{base_url}/api/app/delete/errorlog/1/",# ?limit=2&offset=1
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
    res = requests.get(endpoint["url"], params=endpoint["params"])
    print(f"URL: {endpoint['url']}")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
    print("\n")
  except requests.exceptions.RequestException as e:
    print(f"Request to {endpoint['url']} failed: {e}")
# for endpoint in put_endpoints:
#   try:
#     res = requests.put(endpoint["url"], json=endpoint["data"])
#     print(f"URL: {endpoint['url']}")
#     print(f"Status Code: {res.status_code}")
#     print(f"Response: {res.text}")
#     print("\n")
#   except requests.exceptions.RequestException as e:
#     print(f"Request to {endpoint['url']} failed: {e}")
# for endpoint in delete_endpoints:
#   try:
#     res = requests.delete(endpoint["url"])
#     print(f"URL: {endpoint['url']}")
#     print(f"Status Code: {res.status_code}")
#     print(f"Response: {res.text}")
#     print("\n")
#   except requests.exceptions.RequestException as e:
#     print(f"Request to {endpoint['url']} failed: {e}")