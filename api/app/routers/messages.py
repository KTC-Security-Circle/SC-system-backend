from fastapi import APIRouter
from ..schemas.message import Message
from typing import List

router = APIRouter()

fake_messages = []


@router.post("/messages/", response_model=Message)
async def send_message(message: Message):
    ai_response = Message(content="This is a simulated AI response.")
    fake_messages.append(message.content)
    fake_messages.append(ai_response.content)
    return ai_response


@router.get("/messages/", response_model=List[Message])
async def get_messages():
    return [Message(content=msg) for msg in fake_messages]
