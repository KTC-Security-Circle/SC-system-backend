import requests
import json

res = requests.post(
  "http://localhost:7071/demo/session/",
  json={"id": 2, "session_name": "Python", "pub_data": None,"user_id": 2},
)
print(res.status_code)
print(res.text)
"""
json={"id": 2, "name": "菅田将暉", "email": "exsample@num.jp", "password": "12345678", "authority": "admin"}, 
json={"id": 3, "message": "テスト用テキスト", "bot_reply": "テスト用返信テキスト" ,"pub_data": None,"session_id": 2},
json={"id": 3, "session_name": "Python", "pub_data": None,"user_id": 2},
json={"id": 3, "error_message": "テキストエラー", "pub_data": None,"session_id": 2},
"""