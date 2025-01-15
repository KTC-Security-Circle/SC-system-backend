import asyncio

import httpx

HTTP_STATUS_OK = 200

# エンドポイントURLの定義
base_url = "http://localhost:7071"

# サインアップ情報
signup_url = f"{base_url}/auth/signup/"
signup_data = {
    "name": "Test User",
    "email": "test@example.jp.com",
    "password": "12345678",
    "authority": "admin",
}

# ログイン情報
login_url = f"{base_url}/auth/login/"
login_data = {"email": "test@example.jp.com", "password": "12345678"}


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0) as session:
        # ログインしてトークンをCookieに保存
        response = await session.post(login_url, json=login_data)

        if response.status_code == HTTP_STATUS_OK:
            print("Login succeeded")

            # Cookieから`access_token`を取得
            token = None
            for cookie in session.cookies.jar:
                if cookie.name == "access_token":
                    token = cookie.value
                    break

            if token:
                print(f"Token from cookie: {token}")
            else:
                print("Token not found in cookies")
                return

        else:
            print("Login failed")
            print(response.text)
            return

    headers = {"Authorization": f"Bearer {token}"}

    url = f"{base_url}/api/input/chat/"

    payload = {
        "message": "これはテストメッセージです",
        "session_id": 2,  # Replace with the actual session ID
    }

    # Streaming response for async output
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            # Check the status code
            print("Status Code:", response.status_code)

            if response.status_code == HTTP_STATUS_OK:
                print("Streaming Response:")
                try:
                    async for chunk in response.aiter_bytes():
                        print(chunk.decode("utf-8"), end="")  # Decode and print each chunk
                except httpx.RequestError as e:
                    print(f"Request error: {e}")
            else:
                # エラーレスポンスを読み取って表示
                error_content = await response.aread()
                print("Error:", error_content.decode("utf-8"))


# 実行
asyncio.run(main())
