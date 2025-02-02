from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

from fastapi import HTTPException, status

from api.logger import getLogger

logger = getLogger(__name__)


class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"


# 権限の優劣を定義
ROLE_HIERARCHY = {Role.ADMIN: 3, Role.STAFF: 2, Role.STUDENT: 1}

T = TypeVar("T")


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
        from api.app.models import User

        @wraps(func)
        async def wrapper(*args: Any, current_user: User | None = None, **kwargs: Any) -> T:
            if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            user_role = Role(current_user.authority)
            user_role_level = ROLE_HIERARCHY.get(user_role)
            required_role_level = ROLE_HIERARCHY.get(min_role)

            if required_role_level is None:
                raise ValueError(f"Role {min_role} is not defined in the ROLE_HIERARCHY")
            if user_role_level is None or user_role_level < required_role_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="You do not have sufficient permissions"
                )
                # どうしてもエラーが出るのでignoreする
            return await func(*args, current_user=current_user, **kwargs)  # type: ignore

        # ここも同様にどうしてもエラーが出るのでignore
        return wrapper  # type: ignore

    return decorator  # デコレータを返す