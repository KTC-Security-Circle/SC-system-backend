from collections.abc import Awaitable, Callable
from enum import Enum
from functools import wraps
from typing import TypeVar

from fastapi import HTTPException, status

from api.app.models import User
from api.logger import getLogger

# ロガーの設定
logger = getLogger(__name__)


# ユーザの権限を定義する列挙型
class Role(str, Enum):
    """
    ユーザの権限を表す列挙型。

    - ADMIN: 管理者
    - STAFF: スタッフ
    - STUDENT: 学生
    """

    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"


# 権限の優劣を定義する辞書
ROLE_HIERARCHY = {
    Role.ADMIN: 3,  # 管理者 (最も高い権限)
    Role.STAFF: 2,  # スタッフ
    Role.STUDENT: 1,  # 学生 (最も低い権限)
}

# ジェネリックな型変数
T = TypeVar("T", bound=Callable[..., Awaitable])


def role_required(min_role: Role) -> Callable[[T], T]:
    """
    指定された最小限の権限を要求するデコレータ。

    Args:
        min_role (Role): この権限以上が必要。

    Returns:
        Callable[[T], T]: 関数をラップしたデコレータ。

    Raises:
        HTTPException:
            - ユーザが認証されていない場合 (401 Unauthorized)。
            - 必要な権限を満たしていない場合 (403 Forbidden)。
    """

    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs) -> Awaitable:
            """
            関数をラップして、権限チェックを行う。

            Args:
                current_user (User, optional): 現在の認証されたユーザ。

            Raises:
                HTTPException:
                    - 401 Unauthorized: 認証情報が提供されていない場合。
                    - 403 Forbidden: 必要な権限を満たしていない場合。
            """
            # ユーザが認証されていない場合は 401 エラーを返す
            if current_user is None:
                logger.warning("Unauthorized access attempt detected.")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            # 現在のユーザの権限を取得し、権限レベルを確認
            user_role = Role(current_user.authority)
            user_role_level = ROLE_HIERARCHY.get(user_role)
            required_role_level = ROLE_HIERARCHY.get(min_role)

            # 権限が不足している場合は 403 エラーを返す
            if user_role_level is None or user_role_level < required_role_level:
                logger.warning(
                    f"Permission denied for user {current_user.id}: " f"required={min_role}, actual={user_role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient permissions"
                )

            # 権限チェックを通過した場合、元の関数を実行
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper  # ラッパー関数をデコレータとして返す

    return decorator  # デコレータを返す
