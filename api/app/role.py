from api.app.models import Users
from typing import Callable
from functools import wraps
from fastapi import HTTPException, status, Depends
from api.app.security.jwt_token import get_current_user
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


# 権限の優劣を定義
ROLE_HIERARCHY = {
    Role.ADMIN: 3,
    Role.EDITOR: 2,
    Role.VIEWER: 1
}


def role_required(min_role: Role):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: Users = Depends(get_current_user), **kwargs):
            try:
                # authorityをRole Enumにキャスト
                user_role = Role(current_user.authority)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid role"
                )

            user_role_level = ROLE_HIERARCHY.get(user_role)
            required_role_level = ROLE_HIERARCHY.get(min_role)

            if user_role_level is None or user_role_level < required_role_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have sufficient permissions"
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
