from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class ErrorLog(BaseModel):
    id: int
    error_message: str
    pub_data: Optional[datetime]
    session_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "error_message": "Test error",
                "pub_data": "2024-06-29T12:34:56",
                "session_id": 1
            }
        }
    }


class ChatLog(BaseModel):
    id: int
    message: str
    bot_reply: Optional[str]
    pub_data: Optional[datetime]
    session_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "message": "Hello, world!",
                "bot_reply": "Hello!",
                "pub_data": "2024-06-29T12:34:56",
                "session_id": 1
            }
        }
    }


class Sessions(BaseModel):
    id: int
    session_name: str
    pub_data: Optional[datetime]
    user_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "session_name": "Test Session",
                "pub_data": "2024-06-29T12:34:56",
                "user_id": 1
            }
        }
    }


class Users(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str
    authority: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
                "authority": "admin"
            }
        }
    }
