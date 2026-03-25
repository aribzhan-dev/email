from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    receiver_email: EmailStr
    subject: str = Field(..., max_length=255)
    body: str


class MessageResponse(BaseModel):
    id: int
    sender_email: str
    receiver_email: str
    subject: str
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}