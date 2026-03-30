from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.common.enums.message_type import MessageType


class Media(BaseModel):
    url: Optional[str] = None
    mime: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    type: MessageType
    text: Optional[str] = None
    media: Optional[Media] = None
    sender_id: int
    timestamp: datetime
    is_seen: bool
    seen_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SendMessageSchema(BaseModel):
    text: str
    reply_to: Optional[int] = None


class SendMediaSchema(BaseModel):
    url: str
    caption: Optional[str] = None
    file_name: str
    mime: str
    size: int
    reply_to: Optional[int] = None


class PaginatedMessageResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    page: int
    limit: int