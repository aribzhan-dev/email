from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.common.enums.message_type import MessageType


class ChatCreate(BaseModel):
    user_ids: List[int]
    is_group: bool = False


class ChatResponse(BaseModel):
    id: int
    is_group: bool

    class Config:
        from_attributes = True



class LastMessage(BaseModel):
    id: int
    text: Optional[str]
    type: MessageType
    sender_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatListItem(BaseModel):
    chat_id: int
    is_group: bool
    last_message: Optional[LastMessage]
    unread_count: int

    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    chats: List[ChatListItem]