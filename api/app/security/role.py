from enum import Enum
from functools import wraps

from fastapi import HTTPException, status

from api.logger import getLogger

logger = getLogger(__name__)
class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"


# 権限の優劣を定義
ROLE_HIERARCHY = {
    Role.ADMIN: 3,
    Role.STAFF: 2,
    Role.STUDENT: 1
}


def role_required(min_role: Role):
    from api.app.models import User
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )

            user_role = Role(current_user.authority)
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
