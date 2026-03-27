from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True