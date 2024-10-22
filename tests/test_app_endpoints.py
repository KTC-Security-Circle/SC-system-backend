import requests
import json

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# サインアップ情報
signup_url = f"{base_url}/api/signup/"
signup_data = {
    "name": "Test User",
    "email": "test@example.jp.com",
    "password": "12345678",
    "authority": "admin"
}

# ログイン情報
login_url = f"{base_url}/api/login/"
login_data = {
    "email": "test@example.jp.com",
    "password": "12345678"
}

# get_current_userAPI
get_current_user_url = f"{base_url}/api/user/me"

# サインアップしてユーザーを登録
# response = requests.post(signup_url, json=signup_data)
# if response.status_code == 200:
#     print("Signup successful")
# else:
#     print("Signup failed")
#     print(response.text)
#     exit()

with requests.Session() as session:
    # ログインしてトークンをCookieに保存
    response = session.post(login_url, json=login_data)

    if response.status_code == 200:
        print("Login succeeded")

        # Cookieから`access_token`を取得
        cookies = session.cookies.get_dict()
        token = cookies.get('access_token')  # access_tokenというCookie名を指定

        if token:
            print(f"Token from cookie: {token}")
        else:
            print("Token not found in cookies")
            exit()

    else:
        print("Login failed")
        print(response.text)
        exit()

headers = {
    "Authorization": f"Bearer {token}"
}

#現在のユーザー情報を取得
response = requests.get(get_current_user_url,headers=headers)
if response.status_code == 200:
    print("Current User")
    current_user = response.json()
    print(current_user)
    print(type(current_user))
else:
    print("GetUser failed")
    print(response.text)
    exit()

# 各エンドポイントに対するデータ
post_endpoints = [
    # {
    #     "url": f"{base_url}/api/app/input/user/",
    #     "data": {"name": "aaaaaa", "email": "exsample@num.jp", "password": "12345678", "authority": "admin"}
    # },
    # {
    #     "url": f"{base_url}/api/app/input/session/",
    #     "data": {"session_name": "Python", "pub_data": None}
    # },
    {
        "url": f"{base_url}/api/app/input/chat/",
        "data": {"message": "あなたの役割を教えてください", "pub_data": None, "session_id": 1}
    },
    # {
    #     "url": f"{base_url}/api/app/input/errorlog/",
    #     "data": {"error_message": "テキストエラー", "pub_data": None, "session_id": 1}
    # }
]
get_endpoints = [
    # {
    #     "url": f"{base_url}/api/app/view/user/",
    #     "params": {
    #         "name": "aaaaaa",
    #         "limit": 2,
    #         "offset": 1
    #     }
    # },
    {
        "url": f"{base_url}/api/app/view/chat/",
        "params": {
            "session_id": 1,
            "limit": 1,
            "offset": 2
        }
    },
    # {
    #     "url": f"{base_url}/api/app/view/session/",
    #     "params": {
    #         "user_id": 2,
    #         "limit": 3,
    #         "offset": 1
    #     }
    # },
    # {
    #     "url": f"{base_url}/api/app/view/errorlog/",
    #     "params": {
    #         "session_id": 5,
    #         "limit": 3,
    #         "offset": 1
    #     }
    # }
]

put_endpoints = [
    {
        "url": f"{base_url}/api/app/update/user/{current_user['id']}/",
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
        "url": f"{base_url}/api/app/delete/user/1/"  # {current_user['id']}
    },
    {
        "url": f"{base_url}/api/app/delete/chat/1/"
    },
    {
        "url": f"{base_url}/api/app/delete/session/1/"
    },
    {
        "url": f"{base_url}/api/app/delete/errorlog/1/"
    }
]

# 各エンドポイントにPOSTリクエストを送信
for endpoint in post_endpoints:
    try:
        res = requests.post(
            endpoint["url"], json=endpoint["data"], headers=headers)
        print(f"URL: {endpoint['url'],headers}")
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        print("\n")
    except requests.exceptions.RequestException as e:
        print(f"Request to {endpoint['url']} failed: {e}")

# 各エンドポイントにGETリクエストを送信
for endpoint in get_endpoints:
    try:
        res = requests.get(
            endpoint["url"], params=endpoint["params"], headers=headers)
        print(f"URL: {endpoint['url']}")
        print(f"Params: {endpoint['params']}")
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        print("\n")
    except requests.exceptions.RequestException as e:
        print(f"Request to {endpoint['url']} failed: {e}")

# # 各エンドポイントにPUTリクエストを送信
# for endpoint in put_endpoints:
#     try:
#         res = requests.put(
#             endpoint["url"], json=endpoint["data"], headers=headers)
#         print(f"URL: {endpoint['url']}")
#         print(f"Status Code: {res.status_code}")
#         print(f"Response: {res.text}")
#         print("\n")
#     except requests.exceptions.RequestException as e:
#         print(f"Request to {endpoint['url']} failed: {e}")

# # 各エンドポイントにDELETEリクエストを送信
# for endpoint in delete_endpoints:
#     try:
#         res = requests.delete(endpoint["url"], headers=headers)
#         print(f"URL: {endpoint['url']}")
#         print(f"Status Code: {res.status_code}")
#         print(f"Response: {res.text}")
#         print("\n")
#     except requests.exceptions.RequestException as e:
#         print(f"Request to {endpoint['url']} failed: {e}")
