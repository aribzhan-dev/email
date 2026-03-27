from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    text: Optional[str] = None
    reply_to_id: Optional[int] = None


class AttachmentResponse(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    file_size: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: Optional[str]
    message_type: str
    created_at: datetime
    attachments: List[AttachmentResponse] = []

    class Config:
        from_attributes = True